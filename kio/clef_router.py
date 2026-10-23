"""Cloudflare Clef decision-model router."""

import json
import math
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

    def _response_diagnostics(self, response, body, json_valid):
        """Return safe response-shape diagnostics, never response contents."""
        top = sorted(body) if isinstance(body, dict) else []
        result = body.get("result") if isinstance(body, dict) else None
        answers = result.get("answers") if isinstance(result, dict) else None
        errors = body.get("errors") if isinstance(body, dict) else None
        error_fields = sorted(errors[0]) if isinstance(errors, list) and errors and isinstance(errors[0], dict) else []
        error_text = ""
        if isinstance(errors, list) and errors and isinstance(errors[0], dict):
            code = errors[0].get("code")
            message = errors[0].get("message")
            if code is not None or message is not None:
                error_text = f" error_code={code!r} error_message={str(message)[:160]!r}"
        return (f"http_status={response.status_code} json_valid={json_valid} "
                f"top_fields={top} result_fields={sorted(result) if isinstance(result, dict) else []} "
                f"answers_fields={sorted(answers) if isinstance(answers, dict) else []} "
                f"errors_fields={error_fields}{error_text}")

    @staticmethod
    def _request_error_status(exc):
        """Classify transport failures without exposing URLs or credentials."""
        detail = str(exc).lower()
        if "winerror 10051" in detail or "unreachable network" in detail:
            return "network_unreachable"
        if "name resolution" in detail or "nodename nor servname" in detail:
            return "dns_failure"
        if "certificate" in detail or "ssl" in detail:
            return "tls_error"
        if "timed out" in detail or "timeout" in detail:
            return "request_timeout"
        return f"request_error_{type(exc).__name__}"

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
            try:
                body = response.json()
                json_valid = True
            except (ValueError, json.JSONDecodeError):
                body = {}
                json_valid = False
            diagnostics = self._response_diagnostics(response, body, json_valid)
            if response.status_code in (401, 403):
                return self._invalid(raw, f"authentication_error: {diagnostics}", started)
            if response.status_code == 429:
                return self._invalid(raw, f"rate_limit_or_free_allowance_error: {diagnostics}", started)
            if not response.ok:
                return self._invalid(raw, f"http_error_{response.status_code}: {diagnostics}", started)
            response.raise_for_status()
            if not json_valid:
                return self._invalid(raw, f"malformed_json: {diagnostics}", started)
            envelope = body.get("result", body) if isinstance(body, dict) else {}
            answers = envelope.get("answers") if isinstance(envelope, dict) else None
            route = answers.get("route") if isinstance(answers, dict) else None
            if not isinstance(route, dict):
                fields = sorted(answers.keys()) if isinstance(answers, dict) else []
                return self._invalid(raw, f"missing_or_malformed_route_answer: answer_fields={fields}; {diagnostics}", started)
            # Clef choice answers expose the selected option as `choice`, with
            # per-option probabilities and a confidence value alongside it.
            selected = route.get("choice")
            probabilities = route.get("probabilities")
            if not isinstance(selected, str) or not isinstance(probabilities, dict):
                return self._invalid(raw, f"missing_or_malformed_route_answer: route_fields={sorted(route)}", started)
            values = {key: probabilities.get(key) for key in ("support", "sales")}
            if (not all(isinstance(value, (int, float)) and math.isfinite(float(value)) for value in values.values())
                    or selected.strip().lower() not in values):
                return self._invalid(raw, "missing_or_invalid_route_choice_or_probabilities", started)
            label = selected.strip().lower()
            output = validate_output(label, self.name, (time.perf_counter() - started) * 1000)
            confidence = route.get("confidence", values[label])
            if not isinstance(confidence, (int, float)) or not math.isfinite(float(confidence)):
                return self._invalid(raw, "missing_or_invalid_route_confidence", started)
            output.confidence = float(confidence)
            output.raw = raw
            return output
        except requests.Timeout:
            return self._invalid("", "request_timeout", started)
        except requests.RequestException as exc:
            return self._invalid("", self._request_error_status(exc), started)
        except (ValueError, TypeError, KeyError, json.JSONDecodeError):
            return self._invalid("", "malformed_response", started)

