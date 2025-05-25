import requests
import os
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

PINATA_API_KEY = os.getenv("PINATA_API_KEY")
PINATA_SECRET_API_KEY = os.getenv("PINATA_SECRET_API_KEY")

if not PINATA_API_KEY or not PINATA_SECRET_API_KEY:
    raise EnvironmentError("Pinata API credentials not found in .env file")

def upload_to_ipfs(data_dict):
    url = "https://api.pinata.cloud/pinning/pinJSONToIPFS"
    headers = {
        "Content-Type": "application/json",
        "pinata_api_key": PINATA_API_KEY,
        "pinata_secret_api_key": PINATA_SECRET_API_KEY
    }

    payload = {
        "pinataOptions": {"cidVersion": 1},
        "pinataContent": data_dict
    }

    response = requests.post(url, headers=headers, data=json.dumps(payload))

    if response.status_code == 200:
        ipfs_hash = response.json()["IpfsHash"]
        return ipfs_hash  # ✅ Return plain string
    else:
        raise Exception(f"Pinata upload failed: {response.text}")
