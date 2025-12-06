import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

import urllib.parse

load_dotenv()
# Hardcode the credentials from user input to ensure we construct a valid URI specifically for this detailed debugging
user = "vrushabhbaravkar2005"
# Trying the most likely password: "vrushabh@2005"
pw = "vrushabh@2005"
escaped_pw = urllib.parse.quote_plus(pw)
# Also trying with brackets just in case
pw_brackets = "<vrushabh@2005>"
escaped_pw_brackets = urllib.parse.quote_plus(pw_brackets)

cluster = "cluster0.4jbyjx5.mongodb.net"
uri_1 = f"mongodb+srv://{user}:{escaped_pw}@{cluster}/orchestrator?appName=Cluster0"
uri_2 = f"mongodb+srv://{user}:{escaped_pw_brackets}@{cluster}/orchestrator?appName=Cluster0"

async def ping(uri, label):
    print(f"Testing {label}...")
    try:
        client = AsyncIOMotorClient(uri, serverSelectionTimeoutMS=5000)
        await client.server_info()
        print(f"SUCCESS: Connected using {label}!")
        return True
    except Exception as e:
        print(f"FAIL {label}: {type(e).__name__}: {e}")
        return False

if __name__ == "__main__":
    if asyncio.run(ping(uri_1, "Password 'vrushabh@2005'")):
        print(f"CORRECT_URI={uri_1}")
    elif asyncio.run(ping(uri_2, "Password '<vrushabh@2005>'")):
        print(f"CORRECT_URI={uri_2}")
    else:
        print("Both passwords failed.")
