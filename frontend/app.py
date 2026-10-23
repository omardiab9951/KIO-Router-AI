# Project root is the parent of this file's folder.
# Add it so imports work when launched from the System folder.
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import os

import streamlit as st

from kio import clef_router as clef_module
from kio.clef_router import ClefRouter
from kio.config import EXPECTED_CONTENT_HASH, PROJECT_DIR
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
    """Keep examples out of the dataset without using its labels or splits."""
    messages = {str(value).strip().casefold() for value in get_all_messages()["Message"]}
    return [example for example in EXAMPLES if example.strip().casefold() not in messages]


def _router(mode: str, mock: bool):
    if mode == "ML classifier":
        return MLRouter()
    clef_module.KIO_MOCK = mock
    return ClefRouter()


def _render_output(message: str, router, title: str):
    output, agent = dispatch(message, router)
    st.subheader(title)
    if output.status != "ok" or output.label == "invalid":
        if output.status.startswith("model_missing"):
            st.info("The ML model is not trained yet. Run: python ml_model/train_ml_model.py")
        else:
            st.error(f"Routing failed: {output.status}")
    else:
        st.metric("Flag", output.flag)
        st.write(f"**Label:** {output.label.title()}")
        st.write(f"**Simulated agent:** {agent or 'none'}")
    confidence = "Not available" if output.confidence is None else f"{output.confidence:.3f}"
    st.write(f"**Confidence:** {confidence}")
    st.write(f"**Latency:** {output.latency_ms:.2f} ms")
    st.write(f"**Validation status:** {output.status}")
    with st.expander("Raw output"):
        st.code(output.raw or "(no raw output)")
    return output, agent


def _record(mode: str, output, agent):
    st.session_state.history.append({
        "Mode": mode,
        "Label": output.label,
        "Flag": output.flag,
        "Status": output.status,
        "Latency (ms)": round(output.latency_ms, 2),
        "Agent": agent or "none",
    })


def _select_example(example: str):
    """Set the text before Streamlit creates the text-area widget again."""
    st.session_state.message = example


def main():
    st.set_page_config(page_title="Agent KIO Intent Router")
    st.title("Agent KIO Intent Router")
    if "history" not in st.session_state:
        st.session_state.history = []
    if "message" not in st.session_state:
        st.session_state.message = ""

    with st.sidebar:
        mode = st.radio("Router", ["ML classifier", "Decision model (Clef)", "Compare both"])
        mock = st.checkbox("Mock mode", value=True, disabled=(mode == "ML classifier"))
        st.caption("The correct labels are never sent to any model.")
        if mode != "ML classifier" and mock:
            st.warning("MOCK MODE: not real model output")

    st.text_area("Customer message", key="message", height=120)
    st.caption("Invented examples:")
    examples = _safe_examples()
    for index, example in enumerate(examples):
        st.button(
            example,
            key=f"example_{index}",
            on_click=_select_example,
            args=(example,),
        )

    if st.button("Route message", type="primary"):
        message = st.session_state.message.strip()
        if not message:
            st.error("Enter a customer message first.")
        elif mode == "Compare both":
            left, right = st.columns(2)
            with left:
                ml_output, ml_agent = _render_output(message, MLRouter(), "ML classifier")
            with right:
                clef_output, clef_agent = _render_output(message, _router(mode, mock), "Decision model (Clef)")
            _record("ML classifier", ml_output, ml_agent)
            _record("Decision model (Clef)", clef_output, clef_agent)
            if ml_output.label != "invalid" and clef_output.label != "invalid" and ml_output.label != clef_output.label:
                st.warning("The two routers disagree on this message.")
        else:
            output, agent = _render_output(message, _router(mode, mock), mode)
            _record(mode, output, agent)

    st.subheader("Session history")
    if st.session_state.history:
        st.dataframe(st.session_state.history, use_container_width=True)
    else:
        st.info("No routed messages yet.")

    info_tab, = st.tabs(["Model info"])
    with info_tab:
        st.write("**ML pipeline:** TF-IDF word 1–2 grams → 2D TruncatedSVD → degree-2 polynomial features → StandardScaler → LogisticRegression.")
        st.write("**Decision model:** Cloudflare Clef (`@cf/cloudflare/clef`).")
        instructions = (PROJECT_DIR / "kio" / "routing_instructions.md").read_text(encoding="utf-8")
        st.code("\n".join(instructions.splitlines()[:5]))
        st.write(f"**Dataset content hash:** `{EXPECTED_CONTENT_HASH}`")


if __name__ == "__main__":
    main()

