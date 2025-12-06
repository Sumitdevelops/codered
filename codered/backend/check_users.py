import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from models import User
from dotenv import load_dotenv
import certifi

load_dotenv()

async def check_users():
    uri = os.getenv("MONGODB_URI")
    client = AsyncIOMotorClient(uri, tlsCAFile=certifi.where())
    await init_beanie(database=client.orchestrator, document_models=[User])
    
    count = await User.count()
    print(f"User count in DB: {count}")
    if count > 0:
        users = await User.find_all().to_list()
        print("Existing users:", [u.username for u.username in users])

if __name__ == "__main__":
    asyncio.run(check_users())
