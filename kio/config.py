"""Small configuration helpers. Secrets are read but never printed."""

import os
from pathlib import Path

from dotenv import load_dotenv

PROJECT_DIR = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_DIR / ".env")

CLOUDFLARE_ACCOUNT_ID = os.getenv("CLOUDFLARE_ACCOUNT_ID", "")
CLOUDFLARE_API_TOKEN = os.getenv("CLOUDFLARE_API_TOKEN", "")
KIO_MOCK = os.getenv("KIO_MOCK", "0") == "1"
KIO_CLEF_MODEL = os.getenv("KIO_CLEF_MODEL", "clef")

# This hash covers the canonical CSV content, not the Excel container bytes.
EXPECTED_CONTENT_HASH = "9a655603b371639eafbef19719046355ed8759011cd5cf532cbce01dbf900484"



