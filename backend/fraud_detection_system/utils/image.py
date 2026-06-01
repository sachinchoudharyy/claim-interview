import cv2

# =====================================================
# RGB
# =====================================================

def to_rgb(image):

    return cv2.cvtColor(
        image,
        cv2.COLOR_BGR2RGB
    )

# =====================================================
# GRAY
# =====================================================

def to_gray(image):

    return cv2.cvtColor(
        image,
        cv2.COLOR_BGR2GRAY
    )