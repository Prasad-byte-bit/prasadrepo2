import subprocess
import sys

# ---------------- INSTALL REQUIRED MODULES ---------------- #
def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

# Auto-install missing modules
try:
    import requests
except ModuleNotFoundError:
    print("requests module missing. Installing...")
    install("requests")
    import requests

import xml.etree.ElementTree as ET  # built-in, safe


# ---------------- QUALYS CONFIG ---------------- #

QUALYS_API_URL = "https://qualysapi.qg3.apps.qualys.com/api/3.0/fo/report/index.php"

USERNAME = "avagt2qv"
PASSWORD = "HclTechVM@123"
# ---------------- VALIDATE CONNECTION ---------------- #

def validate_connection():
    print("Validating connection to Qualys (API 3.0)...")

    try:
        response = requests.post(
            QUALYS_API_URL,
            auth=(USERNAME, PASSWORD),
            timeout=60,
            data={"action": "list"},           # API 3.0 still accepts same param
            headers={"X-Requested-With": "Python Requests"}
        )

        if response.status_code != 200:
            print(f"❌ Connection failed: HTTP {response.status_code}")
            print(response.text)
            return False

        print("✅ Connected to Qualys API 3.0 successfully!")

        # Optional: parse XML to confirm valid response
        try:
            ET.fromstring(response.text)
            print("📄 Report list XML parsed successfully.")
        except:
            print("⚠ Received response but XML parsing failed. Check format:")
            print(response.text)

        return True

    except Exception as e:
        print(f"❌ Error connecting to Qualys: {e}")
        return False


if __name__ == "__main__":
    validate_connection()
