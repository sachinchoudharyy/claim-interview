from fraud_detection_system.config import (
    FINAL_SCORE_WEIGHTS,
    get_verdict
)

# =====================================================
# FINAL SCORE
# =====================================================

def calculate_final_score(results):

    final_score = int(

        (
            results["metadata"]["score"]
            *
            FINAL_SCORE_WEIGHTS["metadata"]
        )

        +

        (
            results["ela"]["score"]
            *
            FINAL_SCORE_WEIGHTS["ela"]
        )

        +

        (
            results["mantranet"]["score"]
            *
            FINAL_SCORE_WEIGHTS["mantranet"]
        )

        +

        (
            results["copy_move"]["score"]
            *
            FINAL_SCORE_WEIGHTS["copy_move"]
        )

        +

        (
            results["face_tamper"]["score"]
            *
            FINAL_SCORE_WEIGHTS["face_tamper"]
        )
        +

        (
            results["ai_detection"]["score"]
            *
            FINAL_SCORE_WEIGHTS["ai_detection"]
        )

    )

    final_score = min(final_score, 100)

    return {
        "score": final_score,
        "verdict": get_verdict(final_score)
    }