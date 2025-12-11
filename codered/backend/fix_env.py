import os
from dotenv import load_dotenv, set_key
import urllib.parse

# 1. Load current env to see what we get
load_dotenv()
uri = os.getenv("MONGODB_URI")
print(f"Current URI seen by Python: {uri}")

# 2. Construct the CORRECT URI using code to be 100% sure
user = "vrushabhbaravkar2005"
pw = "vrushabh@2005" 
# NOTE: If user actually meant <vrushabh@2005>, change pw to "<vrushabh@2005>"
escaped_pw = urllib.parse.quote_plus(pw)
correct_uri = f"mongodb+srv://{user}:{escaped_pw}@cluster0.4jbyjx5.mongodb.net/orchestrator?appName=Cluster0"

print(f"Correct URI should be:    {correct_uri}")

# 3. Write it back to .env raw
with open(".env", "w") as f:
    f.write(f'MONGODB_URI="{correct_uri}"\n')

print("Updated .env file.")
