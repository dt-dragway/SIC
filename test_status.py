import requests
import json
import jwt
from datetime import datetime, timedelta

# Create a valid token
token = jwt.encode(
    {"sub": "1", "exp": datetime.utcnow() + timedelta(days=1)}, 
    "b8c3d7e2f1a59046a297b4d3e5f68a12c49b8e7df0a91c3b5d7e6f8a02419c8d", 
    algorithm="HS256"
)

res = requests.get('http://localhost:8001/api/v1/automated-trading/status', headers={'Authorization': f'Bearer {token}'})
print("STATUS API:", res.json())

res2 = requests.get('http://localhost:8001/api/v1/automated-trading/settings', headers={'Authorization': f'Bearer {token}'})
print("SETTINGS API:", res2.json())

