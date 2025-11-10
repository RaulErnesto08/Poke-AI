import streamlit as st
from utils.ui import page_header
from utils.api import api_register, api_login, api_me
from utils.auth import set_tokens, set_me, is_authenticated

st.set_page_config(page_title="Register", page_icon="📝", layout="centered")

page_header("📝 Registro", "Crea una cuenta nueva")

if is_authenticated():
    st.info("Ya tienes sesión activa. Redirigiendo…")
    try:
        st.switch_page("pages/3_Pokedex.py")
    except Exception:
        st.stop()

with st.form("register_form"):
    email = st.text_input("Email", autocomplete="email")
    password = st.text_input("Password", type="password")
    submitted = st.form_submit_button("Crear cuenta")

    if submitted:
        ok, data = api_register(email, password)
        if ok:
            st.success("Cuenta creada ✅. Iniciando sesión…")
            ok2, data2 = api_login(email, password)
            if ok2 and data2:
                set_tokens(data2["access_token"], data2["refresh_token"])
                ok_me, me = api_me(data2["access_token"])
                set_me(me if ok_me else None)
                try:
                    st.switch_page("pages/3_Pokedex.py")
                except Exception:
                    st.experimental_rerun()
            else:
                st.warning("La cuenta fue creada, pero el login falló. Ve a Login.")
        else:
            st.error(f"❌ {data.get('detail','No se pudo registrar')}")

if st.button("Volver a Login"):
    try:
        st.switch_page("pages/1_Login.py")
    except Exception:
        st.experimental_rerun()