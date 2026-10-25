"""Polished Streamlit frontend for the Agent KIO intent router."""

from pathlib import Path
import sys
from datetime import datetime

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
    ("Support", "My internet is down and I need help with my existing service."),
    ("Sales", "I want a new fiber package for my home."),
    ("Mixed intent", "My current service is down, and I am also considering a faster package."),
    ("Negation", "I am not interested in TV; please give me the internet prices."),
]
ROUTERS = {"ml": "Traditional ML", "clef": "Clef decision model", "mock": "Mock keyword"}


def _safe_examples():
    messages = {str(value).strip().casefold() for value in get_all_messages()["Message"]}
    return [(kind, text) for kind, text in EXAMPLES if text.casefold() not in messages]


def _router(choice: str):
    if choice == "ml":
        return MLRouter()
    if choice == "mock":
        clef_module.KIO_MOCK = True
        return ClefRouter()
    clef_module.KIO_MOCK = False
    return ClefRouter()


def _inject_styles():
    st.markdown("""
    <style>
    .hero { padding: 1.2rem 1.4rem; border: 1px solid #E3D9F7; border-radius: 18px;
            background: linear-gradient(135deg, #FFFFFF 0%, #EDE7FB 100%); margin-bottom: 1.2rem; }
    .hero h1 { color: #1F1B2E; margin: 0; font-size: 2.1rem; text-align: center; }
    .hero p { color: #6B6480; margin: .35rem 0 0; text-align: center; }
    .card { background: #FFFFFF; border: 1px solid #E3D9F7; border-radius: 16px;
            padding: 1rem 1.15rem; margin: .5rem 0 1rem; }
    .route-badge { display: inline-block; border-radius: 999px; padding: .35rem .8rem;
                   font-weight: 700; letter-spacing: .02em; }
    .support { color: #5B21B6; background: #EDE7FB; }
    .sales { color: #075985; background: #DFF7F2; }
    .invalid { color: #991B1B; background: #FEE2E2; }
    .muted { color: #6B6480; font-size: .88rem; }
    .footer { color: #6B6480; text-align: center; font-size: .8rem; padding: 1.5rem 0 .5rem; }
    div.stButton > button:hover { border-color: #7C3AED; color: #7C3AED; }
    </style>
    """, unsafe_allow_html=True)


def _header():
    st.markdown("""
    <div class="hero">
      <h1>Agent KIO: Intent Router</h1>
      <p>Message in, routing flag out &nbsp;·&nbsp; 0 = Support &nbsp;·&nbsp; 1 = Sales</p>
    </div>
    """, unsafe_allow_html=True)


def _result_card(output, agent, title="Routing result"):
    label = output.label.title() if output.label != "invalid" else "Invalid"
    badge_class = output.label if output.label in {"support", "sales"} else "invalid"
    confidence = output.confidence
    st.markdown(f'<div class="card"><div class="muted">{title}</div>'
                f'<span class="route-badge {badge_class}">{label}</span></div>',
                unsafe_allow_html=True)
    if output.status != "ok" or output.label == "invalid":
        st.error(f"Routing unavailable: {output.status}")
    metrics = st.columns(4)
    metrics[0].metric("Flag", output.flag if output.flag is not None else "—")
    metrics[1].metric("Simulated agent", agent or "none")
    metrics[2].metric("Latency", f"{output.latency_ms:.2f} ms")
    metrics[3].metric("Validation", output.status)
    st.write(f"**Router:** {output.router_name}")
    if confidence is not None:
        st.write(f"**Confidence:** {confidence:.3f}")
        st.progress(max(0.0, min(1.0, float(confidence))))
    else:
        st.write("**Confidence:** Not available")
    with st.expander("Raw output"):
        st.code(output.raw or "(no raw output)")


def _route(message, choice):
    with st.spinner(f"Routing with {ROUTERS[choice]}…"):
        return dispatch(message, _router(choice))


def _record(output, agent, message, router_name):
    st.session_state.history.append({
        "Time": datetime.now().strftime("%H:%M:%S"),
        "Message": message,
        "Router": router_name,
        "Label": output.label,
        "Flag": output.flag,
        "Confidence": None if output.confidence is None else round(output.confidence, 3),
        "Latency (ms)": round(output.latency_ms, 2),
    })


def _sidebar():
    with st.sidebar:
        st.subheader("Router settings")
        default = KIO_DEFAULT_ROUTER if KIO_DEFAULT_ROUTER in ROUTERS else "ml"
        choice = st.selectbox("Active router", list(ROUTERS), index=list(ROUTERS).index(default),
                              format_func=ROUTERS.get)
        st.caption(f"Active: **{ROUTERS[choice]}**")
        if choice == "mock":
            st.warning("MOCK MODE: results are NOT model output.")
        st.divider()
        st.subheader("About this prototype")
        st.caption("KIO routes the message to a simulated Support or Sales specialist.")
        st.caption("The correct labels are never sent to any model.")
        with st.expander("Model and dataset info"):
            st.write("**ML:** frozen TF-IDF + Logistic Regression")
            st.write("**Clef:** Cloudflare decision model")
            st.code(EXPECTED_CONTENT_HASH)
        return choice


def _message_input():
    st.subheader("Customer message")
    st.text_area("Enter a message to route", key="message", height=140,
                  placeholder="For example: My internet is down…", label_visibility="collapsed")
    st.caption("Try an example:")
    cols = st.columns(4)
    for col, (kind, text) in zip(cols, _safe_examples()):
        if col.button(kind, key=f"example_{kind}", use_container_width=True):
            st.session_state.message = text
            st.rerun()


def _compare(message):
    st.subheader("Compare both routers")
    st.caption("Both routers receive the same message; Clef requires network access and credentials.")
    with st.spinner("Running Traditional ML and Clef…"):
        ml_output, ml_agent = dispatch(message, MLRouter())
        try:
            clef_module.KIO_MOCK = False
            clef_output, clef_agent = dispatch(message, ClefRouter())
        except Exception as exc:
            clef_output, clef_agent = None, None
            st.info(f"Clef is unavailable in this environment ({type(exc).__name__}).")
        if clef_output is not None and clef_output.status != "ok":
            st.info(f"Clef is unavailable: {clef_output.status}. Traditional ML results are still shown.")
    left, right = st.columns(2)
    with left:
        _result_card(ml_output, ml_agent, "Traditional ML")
    with right:
        if clef_output is not None:
            _result_card(clef_output, clef_agent, "Clef decision model")
    if clef_output is not None and ml_output.label != clef_output.label:
        st.warning(f"DISAGREE: ML says {ml_output.label}, while Clef says {clef_output.label}.")
    elif clef_output is not None:
        st.success("AGREE: both routers selected the same route.")


def main():
    st.set_page_config(page_title="Agent KIO: Intent Router", page_icon="🤖", layout="wide")
    _inject_styles()
    _header()
    if "history" not in st.session_state:
        st.session_state.history = []
    if "message" not in st.session_state:
        st.session_state.message = ""

    router_choice = _sidebar()
    _message_input()
    action_left, action_right = st.columns([1, 1])
    route_clicked = action_left.button("Route message", type="primary", use_container_width=True)
    compare_clicked = action_right.button("Compare both", use_container_width=True)
    message = st.session_state.message.strip()
    if route_clicked:
        if not message:
            st.warning("Please enter a customer message before routing.")
        else:
            output, agent = _route(message, router_choice)
            _result_card(output, agent)
            _record(output, agent, message, ROUTERS[router_choice])
    if compare_clicked:
        if not message:
            st.warning("Please enter a customer message before comparing.")
        else:
            _compare(message)

    st.subheader("Session history")
    if st.session_state.history:
        if st.button("Clear history"):
            st.session_state.history = []
            st.rerun()
        st.dataframe(st.session_state.history, use_container_width=True, hide_index=True)
    else:
        st.info("No routed messages yet.")
    st.markdown('<div class="footer">Educational prototype, results based on a 20-message test set.</div>',
                unsafe_allow_html=True)


if __name__ == "__main__":
    main()
