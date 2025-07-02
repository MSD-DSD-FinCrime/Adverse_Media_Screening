import os
from dotenv import load_dotenv

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
SEARCH_ENGINE_ID = os.getenv("GOOGLE_CSE_ID")

NEGATIVE_KEYWORDS = [
    "money laundering",
    "fraud",
    "corruption",
    "bribery",
    "terrorism"
]

# Debug print
print("🔐 API Key Loaded:", GOOGLE_API_KEY is not None)
print("🔍 Search Engine ID Loaded:", SEARCH_ENGINE_ID is not None)
