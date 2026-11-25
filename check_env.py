import os
from dotenv import load_dotenv

load_dotenv()
print(".env in root:", os.path.exists(".env"))
print("Key loaded:", bool(os.environ.get("GROQ_API_KEY")))