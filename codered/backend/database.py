import os
import certifi
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from models import Node, Workload, User # Import models to initialize

async def init_db():
    # Create Motor client
    # Helper: To use Atlas, set MONGODB_URI environment variable
    uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
    
    # Handle SSL checks for MacOS/Atlas
    client = AsyncIOMotorClient(uri, tlsCAFile=certifi.where())
    
    # Initialize Beanie with the Node and Workload document models
    # We'll use a database named 'orchestrator'
    await init_beanie(database=client.orchestrator, document_models=[Node, Workload, User])
