import asyncio
import httpx
from app.infrastructure.database.session import SessionLocal
from app.infrastructure.database.models import User
from app.api.v1.auth import create_access_token

db = SessionLocal()
user = db.query(User).filter(User.email == "admin@sic.com").first()
token = create_access_token(data={"sub": str(user.id)})

async def fetch():
    async with httpx.AsyncClient() as client:
        res = await client.get('http://localhost:8001/api/v1/automated-trading/status', headers={'Authorization': f'Bearer {token}'})
        print("API STATUS RESPONSE:")
        print(res.json())

asyncio.run(fetch())
