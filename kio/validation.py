"""Safe handling of router outputs."""

LABEL_TO_FLAG = {"support": 0, "sales": 1}
ALLOWED_LABELS = set(LABEL_TO_FLAG)


def check_instructions_clean() -> None:
    """Reject instructions that copy any dataset message."""
    from pathlib import Path
    from .data import get_all_messages

    path = Path(__file__).resolve().parent / "routing_instructions.md"
    instructions = path.read_text(encoding="utf-8").strip().lower()
    for message in get_all_messages()["Message"]:
        if str(message).strip().lower() in instructions:
            raise ValueError(f"Routing instructions contain dataset message: {message}")


def validate_output(raw: object, router_name: str, latency_ms: float = 0.0):
    """Normalize a router label; unexpected output becomes invalid."""
    text = "" if raw is None else str(raw).strip()
    label = text.lower()
    if label not in ALLOWED_LABELS:
        from .base import RouterOutput
        return RouterOutput("invalid", None, None, text, latency_ms, "unexpected_label", router_name)
    from .base import RouterOutput
    return RouterOutput(label, LABEL_TO_FLAG[label], None, text, latency_ms, "ok", router_name)

