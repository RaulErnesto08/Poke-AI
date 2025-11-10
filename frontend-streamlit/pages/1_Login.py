import streamlit as st
from utils.ui import page_header
from utils.api import api_login, api_me
from utils.auth import set_tokens, set_me, is_authenticated

st.set_page_config(page_title="Login", page_icon="🔑", layout="centered")

page_header("🔑 Login", "Accede con tu cuenta para continuar")

# Si ya tiene sesión activa -> redirigir
if is_authenticated():
    st.info("Ya tienes sesión activa. Redirigiendo…")
    try:
        st.switch_page("pages/3_Pokedex.py")
    except Exception:
        st.stop()

with st.form("login_form"):
    email = st.text_input("Email", autocomplete="email")
    password = st.text_input("Password", type="password")
    submitted = st.form_submit_button("Login")

    if submitted:
        ok, data = api_login(email, password)
        if ok and data:
            # Guardar tokens
            set_tokens(data["access_token"], data["refresh_token"])

            # Cargar perfil
            ok_me, me = api_me(data["access_token"])
            set_me(me if ok_me else None)

            st.success("Login exitoso ✅")

            try:
                st.switch_page("pages/3_Pokedex.py")
            except Exception:
                st.experimental_rerun()
        else:
            msg = data.get("detail", "Login inválido")
            st.error(f"❌ {msg}")

st.caption("¿No tienes cuenta?")
if st.button("Ir a Registro"):
    try:
        st.switch_page("pages/2_Register.py")
    except Exception:
        st.experimental_rerun()