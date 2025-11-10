# app.py
import streamlit as st
from utils.state import init_session
from utils.auth import is_authenticated

st.set_page_config(page_title="Febara-PokeAPI", page_icon="🐍", layout="centered")
init_session()

# Redirección automática
if is_authenticated():
    try:
        st.switch_page("pages/3_Pokedex.py")
    except Exception:
        st.write("Go to **Welcome** in the left sidebar.")
else:
    try:
        st.switch_page("pages/1_Login.py")
    except Exception:
        st.write("Go to **Login** in the left sidebar.")