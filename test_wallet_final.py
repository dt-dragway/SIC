import asyncio
import httpx
from app.infrastructure.database.session import SessionLocal
from app.infrastructure.database.models import User
from app.api.v1.auth import create_access_token

db = SessionLocal()
user = db.query(User).first()
token = create_access_token(data={"sub": str(user.id)})
db.close()

async def fetch():
    async with httpx.AsyncClient(timeout=20.0) as client:
        res = await client.get('http://localhost:8001/api/v1/practice/wallet', headers={'Authorization': f'Bearer {token}'})
        print("API WALLET RESPONSE:")
        print(res.json())

asyncio.run(fetch())
