import requests
import os
from dotenv import load_dotenv

load_dotenv()

# Get the API_KEY and TOKEN from the environment
api_key = os.getenv("HEALTHILY_API_KEY")
token = os.getenv("HEALTHILY_API_TOKEN")

url = "https://portal.your.md/v4/login"

payload = {
    "name": "Zenith Care",
    "email": "test@gmail.com",
    "email_verified": True,
    "id": "0"
}
headers = {
    "accept": "*/*",
    "content-type": "application/json",
    "Authorization": token,
    "x-api-key": api_key
}

def login():
    response = requests.post(url, json=payload, headers=headers)
    print(response.text)
    return response.text