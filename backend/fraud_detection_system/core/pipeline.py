from fraud_detection_system.core.preprocessing import (
    preprocess_image
)

from fraud_detection_system.core.scoring import (
    calculate_final_score
)

from fraud_detection_system.modules.metadata.analyzer import (
    run_metadata_analysis
)

from fraud_detection_system.modules.ela.detector import (
    run_ela_detection
)



from fraud_detection_system.modules.copy_move.detector import (
    run_copy_move_detection
)

from fraud_detection_system.modules.face_tamper.detector import (
    run_face_tamper_detection
)

from fraud_detection_system.modules.ai_detection.detector import (
    run_ai_detection
)

# =====================================================
# MAIN PIPELINE
# =====================================================

def run_pipeline(image_path):

    try:

        # =====================================================
        # SHARED PREPROCESSING
        # =====================================================

        preprocess_context = preprocess_image(
            image_path
        )

        # =====================================================
        # MODULES
        # =====================================================

        ai_detection_result = run_ai_detection(
            image_path
        )

        metadata_result = run_metadata_analysis(
            image_path
        )

        ela_result = run_ela_detection(
            image_path
        )

        

        copy_move_result = run_copy_move_detection(
            image_path
        )

        face_tamper_result = run_face_tamper_detection(
            image_path
        )

        # =====================================================
        # RESULT COLLECTION
        # =====================================================

        module_results = {

            "ai_detection": ai_detection_result,

            "metadata": metadata_result,

            "ela": ela_result,

            

            "copy_move": copy_move_result,

            "face_tamper": face_tamper_result
        }

        # =====================================================
        # FINAL SCORE
        # =====================================================

        final_analysis = calculate_final_score(
            module_results
        )

        # =====================================================
        # FINAL RESPONSE
        # =====================================================

        return {

            "success": True,

            "final_score": final_analysis["score"],

            "final_verdict": final_analysis["verdict"],

            "modules": module_results
        }

    except Exception as e:

        return {

            "success": False,

            "error": str(e)
        }