import cv2
import torch
import timm
import numpy as np

from torchvision import transforms

from PIL import Image

from fraud_detection_system.config import (
    AI_DETECTION_MODEL_PATH
)

# =====================================================
# DEVICE
# =====================================================

device = torch.device(
    "cuda"
    if torch.cuda.is_available()
    else "cpu"
)

# =====================================================
# MODEL
# =====================================================

model = timm.create_model(
    "tf_efficientnetv2_b2",
    pretrained=False,
    num_classes=2
)

model.load_state_dict(

    torch.load(
        AI_DETECTION_MODEL_PATH,
        map_location=device
    )
)

model.to(device)

model.eval()

# =====================================================
# TRANSFORM
# =====================================================

transform = transforms.Compose([

    transforms.Resize((224, 224)),

    transforms.ToTensor(),

    transforms.Normalize(

        mean=[0.485, 0.456, 0.406],

        std=[0.229, 0.224, 0.225]
    )
])

# =====================================================
# LABELS
# =====================================================

CLASS_NAMES = [
    "AI Generated",
    "Real"
]

# =====================================================
# DETECTION
# =====================================================

def run_ai_detection(image_path):

    image = Image.open(image_path).convert("RGB")

    tensor = transform(image)

    tensor = tensor.unsqueeze(0).to(device)

    with torch.no_grad():

        output = model(tensor)

        probabilities = torch.softmax(
            output,
            dim=1
        )[0]

    predicted_class = torch.argmax(
        probabilities
    ).item()

    confidence = float(
        probabilities[predicted_class] * 100
    )

    label = CLASS_NAMES[predicted_class]

    # =====================================================
    # SCORE
    # =====================================================

    if label == "AI Generated":

        score = int(confidence)

    else:

        score = int(100 - confidence)

    score = max(0, min(score, 100))

    return {

        "module": "ai_detection",

        "label": label,

        "confidence": round(confidence, 2),

        "score": score
    }