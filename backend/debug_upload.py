import requests
import os

BASE_URL = "http://localhost:8000/api/v1"
EMAIL = "admin@sic.com"
PASSWORD = "y2k38*"

def login():
    print("🔑 Iniciando sesión...")
    response = requests.post(
        f"{BASE_URL}/auth/login",
        data={"username": EMAIL, "password": PASSWORD}
    )
    if response.status_code == 200:
        return response.json()["access_token"]
    print(f"❌ Error login: {response.text}")
    return None

def upload_book(token):
    print("📚 Subiendo libro de prueba...")
    
    # Crear archivo dummy
    with open("test_book.txt", "w") as f:
        f.write("Este es un libro de prueba para verificar el sistema de conocimiento.")
    
    files = {'file': ('test_book.txt', open('test_book.txt', 'rb'), 'text/plain')}
    headers = {'Authorization': f"Bearer {token}"}
    
    try:
        response = requests.post(
            f"{BASE_URL}/knowledge/upload-book",
            headers=headers,
            files=files,
            data={"title": "Test Book", "category": "trading"}
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"❌ Error request: {e}")
    finally:
        os.remove("test_book.txt")

if __name__ == "__main__":
    token = login()
    if token:
        upload_book(token)
