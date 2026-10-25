# Project root is the parent of this file's folder.
# Add it so imports work when launched from the System folder.
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import streamlit as st

from kio import clef_router as clef_module
from kio.clef_router import ClefRouter
from kio.config import EXPECTED_CONTENT_HASH, KIO_DEFAULT_ROUTER, PROJECT_DIR
from kio.data import get_all_messages
from kio.ml_router import MLRouter
from kio.router import dispatch

EXAMPLES = [
    "My apartment modem stopped responding after a storm.",
    "Could you quote the monthly cost of a family streaming bundle?",
    "The account portal rejects my new password every time.",
    "I want to purchase a travel data add-on for a short trip.",
    "I am not shopping for an upgrade; please repair my damaged receiver.",
    "The service is down, and I am also considering a faster package.",
]


def _safe_examples():
    messages = {str(value).strip().casefold() for value in get_all_messages()["Message"]}
    return [example for example in EXAMPLES if example.strip().casefold() not in messages]


def _router(choice: str):
    if choice == "ml":
        return MLRouter()
    if choice == "mock":
        clef_module.KIO_MOCK = True
        return ClefRouter()
    clef_module.KIO_MOCK = False
    return ClefRouter()


def _render_output(message: str, router):
    output, agent = dispatch(message, router)
    if output.status != "ok" or output.label == "invalid":
        st.error(f"Routing failed: {output.status}")
    else:
        st.metric("Flag", output.flag)
        st.write(f"**Label:** {output.label.title()}")
        st.write(f"**Simulated agent:** {agent or 'none'}")
    confidence = "Not available" if output.confidence is None else f"{output.confidence:.3f}"
    st.write(f"**Confidence:** {confidence}")
    st.write(f"**Latency:** {output.latency_ms:.2f} ms")
    st.write(f"**Validation status:** {output.status}")
    st.write(f"**Router:** {output.router_name}")
    with st.expander("Raw output"):
        st.code(output.raw or "(no raw output)")
    return output, agent


def _record(output, agent):
    st.session_state.history.append({
        "Label": output.label,
        "Flag": output.flag,
        "Status": output.status,
        "Latency (ms)": round(output.latency_ms, 2),
        "Agent": agent or "none",
        "Router": output.router_name,
    })


def _select_example(example: str):
    st.session_state.message = example


def main():
    st.set_page_config(page_title="Agent KIO Intent Router")
    st.title("Agent KIO Intent Router")
    if "history" not in st.session_state:
        st.session_state.history = []
    if "message" not in st.session_state:
        st.session_state.message = ""

    with st.sidebar:
        choices = {"ml": "Traditional ML", "clef": "Clef decision model", "mock": "Mock keyword"}
        default = KIO_DEFAULT_ROUTER if KIO_DEFAULT_ROUTER in choices else "ml"
        router_choice = st.selectbox("Router", list(choices), index=list(choices).index(default), format_func=choices.get)
        st.caption("The correct labels are never sent to any model.")
        if router_choice == "mock":
            st.warning("MOCK MODE: not real model output")

    st.text_area("Customer message", key="message", height=120)
    st.caption("Invented examples:")
    for index, example in enumerate(_safe_examples()):
        st.button(example, key=f"example_{index}", on_click=_select_example, args=(example,))

    if st.button("Route message", type="primary"):
        message = st.session_state.message.strip()
        if not message:
            st.error("Enter a customer message first.")
        else:
            output, agent = _render_output(message, _router(router_choice))
            output.router_name = f"{output.router_name} ({choices[router_choice]})"
            _record(output, agent)

    st.subheader("Session history")
    if st.session_state.history:
        st.dataframe(st.session_state.history, use_container_width=True)
    else:
        st.info("No routed messages yet.")

    with st.expander("Model info"):
        st.write("**Decision model:** Cloudflare Clef (`@cf/cloudflare/clef`).")
        instructions = (PROJECT_DIR / "kio" / "routing_instructions.md").read_text(encoding="utf-8")
        st.code("\n".join(instructions.splitlines()[:5]))
        st.write(f"**Dataset content hash:** `{EXPECTED_CONTENT_HASH}`")


if __name__ == "__main__":
    main()

