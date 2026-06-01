import requests
import math


# 🔹 CONSTANTS (production tuning)
IP_API_TIMEOUT = 3
MAX_REASON_LENGTH = 5


# 🔹 Get IP-based location
def get_ip_location(ip):
    try:
        if not ip or ip in ["127.0.0.1", "localhost"]:
            print("Skipping IP lookup (local)")
            return None

        if ip.startswith(("192.", "10.", "172.")):
            print("Skipping IP lookup (private)")
            return None

        # 🔹 PRIMARY: ipapi
        try:
            res = requests.get(f"https://ipapi.co/{ip}/json/", timeout=3)

            if res.status_code == 200:
                data = res.json()

                return {
                    "latitude": data.get("latitude"),
                    "longitude": data.get("longitude"),
                    "city": data.get("city"),
                    "country": data.get("country_name")
                }

            else:
                print("ipapi failed:", res.status_code)

        except Exception as e:
            print("ipapi error:", e)

        # 🔹 FALLBACK 1: ipinfo
        try:
            res = requests.get(f"https://ipinfo.io/{ip}/json", timeout=3)

            if res.status_code == 200:
                data = res.json()

                loc = data.get("loc")  # "lat,lon"
                if loc:
                    lat, lon = map(float, loc.split(","))

                    return {
                        "latitude": lat,
                        "longitude": lon,
                        "city": data.get("city"),
                        "country": data.get("country")
                    }

        except Exception as e:
            print("ipinfo error:", e)

        # 🔹 FALLBACK 2: ipwhois
        try:
            res = requests.get(f"http://ipwho.is/{ip}", timeout=3)

            if res.status_code == 200:
                data = res.json()

                if data.get("success"):
                    return {
                        "latitude": data.get("latitude"),
                        "longitude": data.get("longitude"),
                        "city": data.get("city"),
                        "country": data.get("country")
                    }

        except Exception as e:
            print("ipwhois error:", e)

        print("All IP APIs failed")
        return None

    except Exception as e:
        print("IP location error:", e)
        return None


# 🔹 Distance calculation (Haversine)
def calculate_distance_km(lat1, lon1, lat2, lon2):
    try:
        if not all([lat1, lon1, lat2, lon2]):
            return None

        R = 6371  # Earth radius in km

        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)

        a = (
            math.sin(dlat / 2) ** 2 +
            math.cos(math.radians(lat1)) *
            math.cos(math.radians(lat2)) *
            math.sin(dlon / 2) ** 2
        )

        return round(R * (2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))), 2)

    except Exception as e:
        print("Distance calculation error:", e)
        return None


# 🔹 MAIN VALIDATION ENGINE
def validate_location(location, client_ip):
    try:
        gps_lat = location.get("latitude")
        gps_lon = location.get("longitude")
        accuracy = location.get("accuracy")

        # 🔥 NEW: confidence score (0–100)
        confidence = 100

        # reduce confidence based on accuracy
        if accuracy:
            if accuracy > 300:
                confidence -= 50
            elif accuracy > 100:
                confidence -= 25

        reasons = []
        distance_km = None
        risk = "Unknown"

        # 🔹 BASIC VALIDATION
        if not gps_lat or not gps_lon:
            return {
                "distance_km": None,
                "accuracy": accuracy,
                "ip_city": None,
                "ip_country": None,
                "risk": "High",
                "reasons": ["GPS location missing"]
            }

        # 🔹 Get IP location
        ip_loc = get_ip_location(client_ip)

        if ip_loc and ip_loc.get("latitude") and ip_loc.get("longitude"):
            distance_km = calculate_distance_km(
                gps_lat,
                gps_lon,
                ip_loc.get("latitude"),
                ip_loc.get("longitude")
            )

        # 🔥 DISTANCE-BASED RISK
        if distance_km is not None:
            if distance_km > 100:
                risk = "High"
                confidence -= 40
                reasons.append(f"Large GPS-IP mismatch ({distance_km} km)")
            elif distance_km > 20:
                risk = "Medium"
                confidence -= 20
                reasons.append(f"Moderate mismatch ({distance_km} km)")
            else:
                risk = "Low"
                reasons.append("GPS and IP are consistent")

        else:
            risk = "Medium"
            confidence -= 15
            reasons.append("IP location unavailable")

        # 🔥 ACCURACY ADJUSTMENT
        if accuracy:
            if accuracy > 300:
                risk = "High"
                reasons.append(f"Very low GPS accuracy ({accuracy}m)")
            elif accuracy > 100:
                if risk == "Low":
                    risk = "Medium"
                reasons.append(f"Low GPS accuracy ({accuracy}m)")

        # 🔥 FINAL CLEANUP
        reasons = reasons[:MAX_REASON_LENGTH]

        return {
            "distance_km": distance_km,
            "accuracy": accuracy,
            "confidence": max(0, confidence),   # 🔥 NEW
            "ip_city": ip_loc.get("city") if ip_loc else None,
            "ip_country": ip_loc.get("country") if ip_loc else None,
            "risk": risk,
            "reasons": reasons
        }

    except Exception as e:
        print("Location validation error:", e)

        return {
            "distance_km": None,
            "accuracy": None,
            "ip_city": None,
            "ip_country": None,
            "risk": "Unknown",
            "reasons": ["Location validation failed"]
        }