import requests
import json

# Login to get token first (mocking login if needed or using a known token if possible, but let's try to login)
# Or I can just import the verify_token function and bypass auth for a local script? 
# Easier to just hit the DB function directly? No, I want to test the API.

# I will use a simple script that mocks the dependency or assumes I can get a token.
# Actually, I can use the 'test_practice.py' logic or just trust the DB + Code.
# Let's try to login as admin@sic.com (Password usually 'admin123' or similar in seeds)
# If not, I'll relies on the DB proof.

# Let's try to login
try:
    auth = requests.post("http://localhost:8000/api/v1/auth/login", data={"username": "admin@sic.com", "password": "password123"})
    if auth.status_code == 200:
        token = auth.json()["access_token"]
        # Get stats
        stats = requests.get("http://localhost:8000/api/v1/practice/stats", headers={"Authorization": f"Bearer {token}"})
        print("API Response:", stats.json())
    else:
        print("Login failed:", auth.text)
except Exception as e:
    print("Error connecting:", e)
