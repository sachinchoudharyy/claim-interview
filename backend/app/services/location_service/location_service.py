import requests

GEOAPIFY_URL = "https://api.geoapify.com/v1/geocode/reverse"
GEOAPIFY_API_KEY = "65e3bfd1d0894e8a9f2650f86ebdd317"   # 🔥 replace


def reverse_geocode(latitude, longitude):

    try:

        params = {
            "lat": latitude,
            "lon": longitude,
            "apiKey": GEOAPIFY_API_KEY
        }

        response = requests.get(GEOAPIFY_URL, params=params, timeout=5)

        if response.status_code != 200:
            print("Geoapify failed:", response.status_code)
            return {"full_address": None}

        data = response.json()

        features = data.get("features", [])
        if not features:
            return {"full_address": None}

        props = features[0].get("properties", {})

        return {
            "full_address": props.get("formatted"),

            "road": props.get("street"),
            "area": props.get("suburb") or props.get("neighbourhood"),
            "city": props.get("city"),
            "district": props.get("district"),
            "state": props.get("state"),
            "pincode": props.get("postcode")
        }

    except Exception as e:
        print("Geoapify error:", e)

        return {
            "full_address": None
        }