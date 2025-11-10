import streamlit as st
from .state import init_session, reset_session
from utils.api import api_refresh_with_access

def is_authenticated() -> bool:
    init_session()
    return bool(st.session_state.get("access_token"))

def set_tokens(access: str, refresh: str):
    st.session_state.access_token = access
    st.session_state.refresh_token = refresh

def set_me(me: dict | None):
    st.session_state.me = me

def logout():
    reset_session()
    st.success("Logged out ✅")
    try:
        st.switch_page("pages/1_Login.py")
    except Exception:
        st.experimental_rerun()

def require_auth():
    """
    Garantiza que exista un access token válido.
    Si el access_token falta pero hay refresh_token,
    se intenta renovar automáticamente.
    """
    init_session()

    # Si ya hay access token -> OK
    if st.session_state.get("access_token"):
        return

    # Si no hay access, pero hay refresh -> intentar renovar
    refresh_token = st.session_state.get("refresh_token")
    if refresh_token:
        ok, data = api_refresh_with_access(refresh_token)
        if ok and data:
            set_tokens(data["access_token"], data["refresh_token"])
            return

    # Sin access y sin refresh --> login
    try:
        st.switch_page("pages/1_Login.py")
    except Exception:
        st.stop()