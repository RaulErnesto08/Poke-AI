import streamlit as st
from utils.ui import page_header, inject_global_css, sidebar_auth_block, pokemon_card
from utils.auth import require_auth, logout
from utils.api import api_ai_compare

st.set_page_config(page_title="Comparador Inteligente", page_icon="⚔️", layout="wide")

# Requiere login
require_auth()
sidebar_auth_block(on_logout=logout)
inject_global_css()

page_header("⚔️ Comparador Inteligente", "Analiza dos Pokémon con IA")

# Estado
if "cmp_result" not in st.session_state:
    st.session_state.cmp_result = None

st.markdown("""
Compara dos Pokémon y obtén:
- análisis detallado
- ventajas y desventajas
- comparativa de estadísticas
- predicción del ganador
""")

st.markdown("---")

colA, colB = st.columns(2)

with colA:
    pk_a = st.text_input("Pokémon A (nombre o ID)", key="compare_a", placeholder="Ej: charizard")

with colB:
    pk_b = st.text_input("Pokémon B (nombre o ID)", key="compare_b", placeholder="Ej: blastoise")

center = st.columns([1, 1, 1])
with center[1]:
    compare_btn = st.button("⚔️ Comparar ✨")

if compare_btn:
    if not pk_a.strip() or not pk_b.strip():
        st.error("Debes ingresar ambos Pokémon.")
    else:
        with st.spinner("Comparando con IA..."):
            ok, result = api_ai_compare(pk_a.strip(), pk_b.strip(), st.session_state.access_token)
            if ok:
                st.session_state.cmp_result = result
            else:
                st.error(result.get("detail", "Error en la comparación."))


# ─────────────────────────────────────────
# Mostrar resultado
# ─────────────────────────────────────────
if st.session_state.cmp_result:
    result = st.session_state.cmp_result

    st.markdown("---")
    st.markdown("## 📊 Análisis detallado")
    st.markdown(result["summary"])

    st.markdown("---")
    st.markdown(f"## 🏆 Predicción del ganador: **{result['winner'].capitalize()}**")

    st.markdown("---")
    
    col1, col2 = st.columns(2)

    # Pokémon A
    with col1:
        st.markdown(f"### 🅰️ {result['a']['name'].capitalize()}")
        pokemon_card(result["a"])

        # Add to collection button
        if result["a"].get("id") and st.session_state.access_token:
            if st.button(f"➕ Agregar {result['a']['name'].capitalize()} a mi colección", key="cmp_add_a"):
                from utils.api import api_collection_add
                ok_add, resp = api_collection_add(st.session_state.access_token, int(result["a"]["id"]))
                if ok_add:
                    st.success(f"{result['a']['name'].capitalize()} añadido ✅")
                else:
                    detail = (resp or {}).get("detail", "No se pudo agregar")
                    st.error(f"❌ {detail}")

    # Pokémon B
    with col2:
        st.markdown(f"### 🅱️ {result['b']['name'].capitalize()}")
        pokemon_card(result["b"])

        # Add to collection button
        if result["b"].get("id") and st.session_state.access_token:
            if st.button(f"➕ Agregar {result['b']['name'].capitalize()} a mi colección", key="cmp_add_b"):
                from utils.api import api_collection_add
                ok_add, resp = api_collection_add(st.session_state.access_token, int(result["b"]["id"]))
                if ok_add:
                    st.success(f"{result['b']['name'].capitalize()} añadido ✅")
                else:
                    detail = (resp or {}).get("detail", "No se pudo agregar")
                    st.error(f"❌ {detail}")

    st.markdown("---")