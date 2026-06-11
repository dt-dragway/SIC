import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient
from app.main import app

def test_stats():
    client = TestClient(app)
    
    # Authenticate
    login_data = {
        "username": "admin@sic.com",
        "password": "Admin24252026**"
    }
    login_res = client.post("/api/v1/auth/login", data=login_data)
    token = login_res.json()["access_token"]
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Query practice stats
    res = client.get("/api/v1/practice/stats", headers=headers)
    print("Practice Stats Status Code:", res.status_code)
    if res.status_code == 200:
        import json
        print(json.dumps(res.json(), indent=2))

if __name__ == "__main__":
    test_stats()
