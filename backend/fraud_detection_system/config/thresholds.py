# =====================================================
# COMMON VERDICTS
# =====================================================

def get_verdict(score):

    if score <= 20:
        return "Likely Genuine"

    elif score <= 45:
        return "Slightly Suspicious"

    elif score <= 70:
        return "Highly Suspicious"

    return "Likely Forged"