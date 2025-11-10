import streamlit as st

SESSION_KEYS = [
    "access_token",
    "refresh_token",
    "me",
]

def init_session():
    for k in SESSION_KEYS:
        if k not in st.session_state:
            st.session_state[k] = None

def reset_session():
    for k in SESSION_KEYS:
        st.session_state[k] = None