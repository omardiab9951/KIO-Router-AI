"""Cloudflare Clef decision-model router."""

import json
import time
from pathlib import Path

import requests

from .base import BaseRouter, RouterOutput
from .config import CLOUDFLARE_ACCOUNT_ID, CLOUDFLARE_API_TOKEN, KIO_CLEF_MODEL, KIO_MOCK
from .validation import check_instructions_clean, validate_output


class ClefRouter(BaseRouter):
    def __init__(self):
        self.model_id = KIO_CLEF_MODEL.strip() or "clef"
        self.name = f"clef:@cf/cloudflare/{self.model_id}"
        self.endpoint = f"https://api.cloudflare.com/client/v4/accounts/{CLOUDFLARE_ACCOUNT_ID}/ai/run/@cf/cloudflare/{self.model_id}"

    def _instructions(self):
        check_instructions_clean()
        return (Path(__file__).resolve().parent / "routing_instructions.md").read_text(encoding="utf-8").strip()

    def _invalid(self, raw, status, started):
        return RouterOutput("invalid", None, None, raw, (time.perf_counter() - started) * 1000, status, self.name)

    def predict(self, message: str) -> RouterOutput:
        started = time.perf_counter()
        if not isinstance(message, str) or not message.strip():
            return self._invalid("", "empty_message", started)
        if KIO_MOCK:
            lower = message.lower()
            label = "sales" if any(word in lower for word in ("buy", "price", "plan")) else "support"
            output = validate_output(label, self.name, (time.perf_counter() - started) * 1000)
            output.raw = json.dumps({"mock": True, "answer": label})
            output.router_name = f"{self.name}:mock"
            return output
        if not CLOUDFLARE_ACCOUNT_ID or not CLOUDFLARE_API_TOKEN:
            return self._invalid("", "missing_cloudflare_credentials", started)
        try:
            instructions = self._instructions()
            payload = {
                "model": self.model_id,
                "state": f"{instructions}\n\nCustomer message:\n{message}",
                "questions": {"route": {
                    "type": "choice",
                    "instructions": "Which route should handle this customer message?",
                    "criteria": {
                        "support": "Existing problem, complaint, billing, account, or help with an existing service/order.",
                        "sales": "Mainly a new purchase, package, upgrade, price, quote, or promotion.",
                    },
                }},
            }
            response = requests.post(self.endpoint, headers={"Authorization": f"Bearer {CLOUDFLARE_API_TOKEN}"}, json=payload, timeout=60)
            raw = response.text
            if response.status_code in (401, 403):
                return self._invalid(raw, "authentication_error", started)
            if response.status_code == 429:
                return self._invalid(raw, "rate_limit_or_free_allowance_error", started)
            response.raise_for_status()
            body = response.json()
            probabilities = body.get("answers", {}).get("route")
            if not isinstance(probabilities, dict):
                return self._invalid(raw, "missing_or_malformed_route_answer", started)
            values = {key: probabilities.get(key) for key in ("support", "sales")}
            if not all(isinstance(value, (int, float)) for value in values.values()):
                return self._invalid(raw, "missing_route_probabilities", started)
            label = max(values, key=values.get)
            output = validate_output(label, self.name, (time.perf_counter() - started) * 1000)
            output.confidence = float(values[label])
            output.raw = raw
            return output
        except requests.Timeout:
            return self._invalid("", "request_timeout", started)
        except requests.RequestException:
            return self._invalid("", "request_error", started)
        except (ValueError, TypeError, KeyError, json.JSONDecodeError):
            return self._invalid("", "malformed_response", started)

