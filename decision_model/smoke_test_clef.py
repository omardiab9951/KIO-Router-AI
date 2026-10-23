"""One-request live smoke test for the Cloudflare Clef router."""

 # Project root is the parent of this file's folder.
 # Add it so imports work when launched from the System folder.
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import json
import os
import re

def _safe(text: str) -> str:
    """Remove credential-like values before printing API data."""
    text = re.sub(r"Bearer\s+[^\s\"']+", "Bearer [REDACTED]", text, flags=re.I)
    for key in ("CLOUDFLARE_API_TOKEN", "CLOUDFLARE_ACCOUNT_ID"):
        value = os.getenv(key, "")
        if value:
            text = text.replace(value, "[REDACTED]")
    return text


def main() -> int:
    from dotenv import load_dotenv

    load_dotenv()
    if os.getenv("KIO_MOCK", "0") == "1":
        print("Refusing to run: KIO_MOCK=1; this smoke test requires the real Clef API.")
        return 1

    from kio.clef_router import ClefRouter

    message = "My television shows no signal since this morning."
    result = ClefRouter().predict(message)

    if result.status != "ok":
        print(f"Clef smoke test stopped: {result.status}.")
        return 1

    try:
        body = json.loads(result.raw)
    except json.JSONDecodeError:
        body = {}

    answers = body.get("answers", {})
    route = answers.get("route") if isinstance(answers, dict) else None
    model = body.get("model", "unavailable")
    print("HTTP status: 200 (successful router response)")
    print(f"label: {result.label}")
    print(f"flag: {result.flag}")
    print(f"confidence/probabilities: {_safe(json.dumps(route, ensure_ascii=False))}")
    print(f"latency_ms: {result.latency_ms:.2f}")
    print(f"model: {_safe(str(model))}")
    print(f"raw response: {_safe(result.raw)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

