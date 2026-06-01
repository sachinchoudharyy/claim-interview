import cv2

from fraud_detection_system.config import MAX_IMAGE_SIZE

# =====================================================
# LOAD IMAGE
# =====================================================

def load_image(image_path):

    image = cv2.imread(image_path)

    if image is None:

        raise ValueError(
            "Unable to load image."
        )

    return image

# =====================================================
# RESIZE
# =====================================================

def resize_image(image):

    height, width = image.shape[:2]

    max_dimension = max(height, width)

    if max_dimension <= MAX_IMAGE_SIZE:

        return image

    scale = MAX_IMAGE_SIZE / max_dimension

    new_width = int(width * scale)

    new_height = int(height * scale)

    resized = cv2.resize(
        image,
        (new_width, new_height),
        interpolation=cv2.INTER_AREA
    )

    return resized

# =====================================================
# PREPROCESS
# =====================================================

def preprocess_image(image_path):

    image = load_image(image_path)

    image = resize_image(image)

    rgb = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2RGB
    )

    gray = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2GRAY
    )

    denoised = cv2.GaussianBlur(
        gray,
        (5, 5),
        0
    )

    return {

        "path": image_path,

        "original": image,

        "rgb": rgb,

        "gray": gray,

        "denoised": denoised
    }