import cv2
import numpy as np

from insightface.app import FaceAnalysis

app = FaceAnalysis(
    name="buffalo_l"
)

app.prepare(
    ctx_id=0,
    det_size=(640, 640)
)


def cosine_similarity(a, b):

    return np.dot(a, b) / (
        np.linalg.norm(a)
        * np.linalg.norm(b)
    )


def verify_faces(
    doc_path,
    verification_path
):

    img1 = cv2.imread(doc_path)

    img2 = cv2.imread(verification_path)

    faces1 = app.get(img1)

    faces2 = app.get(img2)

    if not faces1:

        return {
            "score": 0,
            "status": "No face in document"
        }

    if not faces2:

        return {
            "score": 0,
            "status": "No face in verification photo"
        }

    emb1 = faces1[0].embedding

    emb2 = faces2[0].embedding

    similarity = cosine_similarity(
        emb1,
        emb2
    )

    score = round(
        float(similarity) * 100,
        2
    )

    if score >= 65:

        status = "Same Person"

    elif score >= 45:

        status = "Likely Same Person"

    else:

        status = "Different Person"

    return {

        "score": score,

        "status": status
    }