import cv2
import numpy as np
import onnxruntime as ort
import mediapipe as mp

# 🔇 Optional: suppress ONNX warnings
ort.set_default_logger_severity(3)

mp_face = mp.solutions.face_detection


class AntiSpoofModel:
    def __init__(self, model_path):
        self.session = ort.InferenceSession(model_path)
        self.input_name = self.session.get_inputs()[0].name
        self.face_detector = mp_face.FaceDetection(
            model_selection=0, min_detection_confidence=0.5
        )

    def extract_face(self, frame):
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        res = self.face_detector.process(rgb)

        if res.detections:
            bbox = res.detections[0].location_data.relative_bounding_box
            h, w, _ = frame.shape

            x = max(0, int(bbox.xmin * w))
            y = max(0, int(bbox.ymin * h))
            bw = int(bbox.width * w)
            bh = int(bbox.height * h)

            face = frame[y:y + bh, x:x + bw]

            if face.size > 0:
                return face

        return frame  # fallback if no face

    def preprocess(self, frame):
        # ✅ CRITICAL FIX: crop face first
        face = self.extract_face(frame)

        # ✅ correct size
        img = cv2.resize(face, (112, 112))

        # ✅ correct normalization
        img = img.astype(np.float32)
        img = (img - 127.5) / 128.0

        # ✅ ONNX format (NCHW)
        img = np.transpose(img, (2, 0, 1))
        img = np.expand_dims(img, axis=0)

        return img

    def predict(self, frame):
        inp = self.preprocess(frame)

        pred = self.session.run(None, {self.input_name: inp})[0]

        raw_score = float(pred[0][0])

        # clamp
        raw_score = max(0.0, min(1.0, raw_score))

        # ✅ CRITICAL FIX: invert (model outputs spoof probability)
        score = 1.0 - raw_score

        return score