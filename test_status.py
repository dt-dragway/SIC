import asyncio
import httpx
from app.infrastructure.database.session import SessionLocal
from app.infrastructure.database.models import User, AutomationConfig
from app.api.v1.auth import create_access_token

db = SessionLocal()
user = db.query(User).filter(User.email == "admin@sic.com").first()
if not user:
    user = db.query(User).first()

token = create_access_token(data={"sub": str(user.id)})

# Imprimir estado real en la BD
config = db.query(AutomationConfig).filter(AutomationConfig.user_id == user.id).first()
if config:
    print(f"DATABASE ENABLED STATUS: {config.enabled}")
else:
    print("NO CONFIG IN DB!")

db.close()

async def fetch():
    async with httpx.AsyncClient(timeout=10.0) as client:
        res = await client.get('http://localhost:8001/api/v1/automated-trading/status', headers={'Authorization': f'Bearer {token}'})
        print("API STATUS RESPONSE:")
        print(res.json())

asyncio.run(fetch())
