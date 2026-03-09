import os
from dotenv import load_dotenv

REGION_NAMES = {
    "eu-central-1": "Europe (Frankfurt)",
    "us-east-1": "US East (N. Virginia)",
    "ap-southeast-1": "Asia Pacific (Singapore)"
}

load_dotenv()

domains_str = os.getenv("DOMAINS", "")
ALLOWED_ORIGINS = [d.strip() for d in domains_str.split(",") if d.strip()]

if not ALLOWED_ORIGINS:
    ALLOWED_ORIGINS = []
