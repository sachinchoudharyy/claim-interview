from PIL import Image
from PIL.ExifTags import TAGS

import cv2
import numpy as np
import piexif

from fraud_detection_system.config import get_verdict

# =====================================================
# METADATA CHECK
# =====================================================

def check_metadata(image_path):

    result = {

        "metadata_found": False,

        "editing_software": None,

        "suspicious": False,

        "software_detected": False
    }

    try:

        img = Image.open(image_path)

        exif = img._getexif()

        if not exif:

            return result

        result["metadata_found"] = True

        suspicious_softwares = [

            "Photoshop",
            "Adobe",
            "Canva",
            "Snapseed",
            "PicsArt",
            "GIMP",
            "Photopea",
            "Pixlr",
            "Remini",
            "Lightroom"
        ]

        for tag, value in exif.items():

            tag_name = TAGS.get(tag, tag)

            if tag_name == "Software":

                result["editing_software"] = str(value)

                result["software_detected"] = True

                for software in suspicious_softwares:

                    if software.lower() in str(value).lower():

                        result["suspicious"] = True

                        break

    except Exception as e:

        result["error"] = str(e)

    return result

# =====================================================
# DPI CHECK
# =====================================================

def check_dpi(image_path):

    result = {

        "dpi": None,

        "suspicious": False,

        "score": 0
    }

    try:

        img = Image.open(image_path)

        dpi = img.info.get("dpi")

        result["dpi"] = dpi

        if dpi:

            if dpi[0] < 70 or dpi[0] > 1200:

                result["suspicious"] = True

                result["score"] += 10

    except Exception as e:

        result["error"] = str(e)

    return result

# =====================================================
# TIMESTAMP CHECK
# =====================================================

def check_timestamp(image_path):

    result = {

        "datetime": None,

        "score": 0
    }

    try:

        img = Image.open(image_path)

        exif = img._getexif()

        if exif:

            for tag, value in exif.items():

                tag_name = TAGS.get(tag, tag)

                if tag_name == "DateTime":

                    result["datetime"] = value

    except Exception as e:

        result["error"] = str(e)

    return result

# =====================================================
# GPS CHECK
# =====================================================

def check_gps(image_path):

    result = {

        "gps_found": False,

        "score": 0
    }

    try:

        img = Image.open(image_path)

        exif = img._getexif()

        if exif:

            for tag, value in exif.items():

                tag_name = TAGS.get(tag, tag)

                if tag_name == "GPSInfo":

                    result["gps_found"] = True

    except Exception as e:

        result["error"] = str(e)

    return result

# =====================================================
# THUMBNAIL CHECK
# =====================================================

def check_thumbnail(image_path):

    result = {

        "thumbnail_found": False,

        "suspicious": False,

        "score": 0
    }

    try:

        exif_dict = piexif.load(image_path)

        thumbnail = exif_dict.get("thumbnail")

        if thumbnail:

            result["thumbnail_found"] = True

        else:

            result["score"] += 5

    except Exception as e:

        result["error"] = str(e)

    return result

# =====================================================
# RECOMPRESSION CHECK
# =====================================================

def check_recompression(image_path):

    result = {

        "multiple_compression_possible": False,

        "variance": None
    }

    try:

        img = cv2.imread(image_path)

        if img is None:

            result["error"] = "Image not loaded"

            return result

        gray = cv2.cvtColor(
            img,
            cv2.COLOR_BGR2GRAY
        )

        variance = np.var(gray)

        result["variance"] = float(variance)

        if variance < 300:

            result["multiple_compression_possible"] = True

        elif variance < 500:

            result["multiple_compression_possible"] = True

    except Exception as e:

        result["error"] = str(e)

    return result

# =====================================================
# JSON SAFE CONVERSION
# =====================================================

def make_json_safe(data):

    if isinstance(data, dict):

        return {

            str(key): make_json_safe(value)

            for key, value in data.items()
        }

    elif isinstance(data, list):

        return [
            make_json_safe(item)
            for item in data
        ]

    elif isinstance(data, tuple):

        return tuple(
            make_json_safe(item)
            for item in data
        )

    # PIL IFDRational
    elif hasattr(data, "numerator") and hasattr(data, "denominator"):

        try:

            return float(data)

        except:

            return str(data)

    elif isinstance(
        data,
        (
            int,
            float,
            str,
            bool,
            type(None)
        )
    ):

        return data

    return str(data)

# =====================================================
# FINAL SCORE
# =====================================================

def generate_metadata_score(

    metadata,
    dpi,
    timestamp,
    gps,
    thumbnail,
    recompression
):

    score = 0

    reasons = []

    if metadata.get("suspicious"):

        score += 40

        reasons.append(
            "Suspicious editing software detected"
        )

    elif not metadata.get("metadata_found"):

        score += 10

        reasons.append(
            "Metadata missing"
        )

    if dpi.get("suspicious"):

        score += 10

        reasons.append(
            "Abnormal DPI detected"
        )

    if thumbnail.get("suspicious"):

        score += 10

        reasons.append(
            "Missing EXIF thumbnail"
        )

    if recompression.get(
        "multiple_compression_possible"
    ):

        score += 15

        reasons.append(
            "Possible recompression detected"
        )

    score = min(score, 100)

    return {

        "module": "metadata",

        "score": score,

        "verdict": get_verdict(score),

        "reasons": reasons,

        "details": make_json_safe({

            "metadata": metadata,

            "dpi": dpi,

            "timestamp": timestamp,

            "gps": gps,

            "thumbnail": thumbnail,

            "recompression": recompression
        })
    }

# =====================================================
# RUN METADATA ANALYSIS
# =====================================================

def run_metadata_analysis(image_path):

    metadata = check_metadata(image_path)

    dpi = check_dpi(image_path)

    timestamp = check_timestamp(image_path)

    gps = check_gps(image_path)

    thumbnail = check_thumbnail(image_path)

    recompression = check_recompression(image_path)

    return generate_metadata_score(

        metadata=metadata,

        dpi=dpi,

        timestamp=timestamp,

        gps=gps,

        thumbnail=thumbnail,

        recompression=recompression
    )