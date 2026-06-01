# midas_model.py
import torch
import numpy as np
import cv2

class MiDaSDepth:
    def __init__(self, model_type="MiDaS_small"):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = torch.hub.load("intel-isl/MiDaS", model_type)
        self.model.to(self.device).eval()
        self.transforms = torch.hub.load("intel-isl/MiDaS", "transforms")
        self.transform = self.transforms.dpt_transform if "DPT" in model_type else self.transforms.small_transform

    def estimate_depth(self, frame_rgb):
        """Estimate depth map for a single RGB frame."""
        frame_rgb = cv2.resize(frame_rgb, (256, 256))
        input_batch = self.transform(frame_rgb).to(self.device)
        with torch.no_grad():
            prediction = self.model(input_batch)
            prediction = torch.nn.functional.interpolate(
                prediction.unsqueeze(1),
                size=frame_rgb.shape[:2],
                mode="bicubic",
                align_corners=False,
            ).squeeze()
        return prediction.cpu().numpy()

# Initialize once
midas_model = MiDaSDepth()
