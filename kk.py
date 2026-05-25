import requests

def locate_mobile(mobile_number):
    API_KEY = "YOUR_API_KEY"
    url = f"http://apilayer.net/api/validate?access_key={API_KEY}&number={mobile_number}"

    response = requests.get(url, timeout=5)
    data = response.json()

    if not data.get("valid"):
        return {"error": "Invalid number"}

    return {
        "country": data["country_name"],
        "location": data["location"],
        "carrier": data["carrier"],
        "line_type": data["line_type"]
    }
