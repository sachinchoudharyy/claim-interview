def compute_fraud_score(liveness_result, audio_result):
    try:
        if not liveness_result or not audio_result:
            return None

        # 🔹 Liveness factors
        liveness_flag = 1 if liveness_result.get("liveness") else 0
        confidence = liveness_result.get("confidence", 0)

        # 🔹 Audio factors
        trust_score = audio_result.get("trust_score", 0) / 100.0
        stress = audio_result.get("stress", 1)
        hesitation = audio_result.get("hesitation", 1)

        # 🔥 FINAL SCORE (balanced)
        final_score = (
            0.40 * liveness_flag +
            0.20 * confidence +
            0.25 * trust_score +
            0.10 * (1 - stress) +
            0.05 * (1 - hesitation)
        )

        final_score = round(final_score * 100, 2)

        # 🔥 CLASSIFICATION
        if final_score >= 75:
            label = "Low Risk"
        elif final_score >= 50:
            label = "Medium Risk"
        else:
            label = "High Risk"

        return {
            "fraud_score": final_score,
            "risk": label
        }

    except Exception as e:
        print("FRAUD SCORE ERROR:", e)
        return None