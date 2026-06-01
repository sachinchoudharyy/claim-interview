import logging

# =====================================================
# LOGGER
# =====================================================

logging.basicConfig(

    level=logging.INFO,

    format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(
    "fraud_detection_system"
)