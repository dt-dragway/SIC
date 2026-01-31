
import requests
import json
from app.config import settings

# 1. Login to get token
base_url = "http://localhost:8000/api/v1"
login_data = {
    "username": settings.admin_email,
    "password": settings.admin_password
}

print(f"Logging in as {login_data['username']}...")
try:
    resp = requests.post(f"{base_url}/auth/login", data=login_data)
    if resp.status_code != 200:
        print(f"Login failed: {resp.status_code} {resp.text}")
        exit(1)
    
    token = resp.json()['access_token']
    print("Login successful.")
    
    # 2. Get Practice Wallet
    headers = {"Authorization": f"Bearer {token}"}
    print("Fetching practice wallet...")
    resp = requests.get(f"{base_url}/practice/wallet", headers=headers)
    
    print(f"Status: {resp.status_code}")
    print("Response:")
    print(json.dumps(resp.json(), indent=2))
    
except Exception as e:
    print(f"Error: {e}")
