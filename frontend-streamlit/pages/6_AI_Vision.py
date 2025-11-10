import streamlit as st
from utils.auth import require_auth, logout
from utils.api import api_ai_identify, api_pokedex_get, api_collection_add
from utils.ui import page_header, inject_global_css, sidebar_auth_block, pokemon_card

st.set_page_config(page_title="AI Vision", page_icon="👁️", layout="wide")

# ---- auth & style ----
require_auth()
sidebar_auth_block(on_logout=logout)
inject_global_css()
page_header("👁️ AI Vision", "Identifica Pokémon desde una imagen usando IA")

# ---- inicializar estado ----
if "ai_image" not in st.session_state:
    st.session_state.ai_image = None

if "ai_result" not in st.session_state:
    st.session_state.ai_result = None

# ---- upload ----
st.subheader("📤 Sube una imagen")
uploaded = st.file_uploader(
    "Selecciona un archivo JPG/PNG",
    type=["jpg", "jpeg", "png"],
    help="Sube una imagen clara de un Pokémon",
)

if uploaded:
    st.session_state.ai_image = uploaded
    # 🔧 usa use_container_width (no use_column_width)
    st.image(uploaded, caption="Imagen cargada", use_container_width=True)
else:
    st.info("Sube una imagen para comenzar.")
    st.stop()

# ---- identify button ----
if st.button("🔍 Identificar Pokémon", type="primary"):
    with st.spinner("Analizando imagen... 🔄"):
        ok, resp = api_ai_identify(st.session_state.access_token, st.session_state.ai_image)

    if not ok:
        st.error(resp.get("detail", "❌ No se pudo procesar la imagen"))
    else:
        st.session_state.ai_result = resp
        st.success("✅ Identificación completa")

# ---- results ----
st.markdown("---")

ai_result = st.session_state.ai_result
if not ai_result:
    st.info("Haz clic en **Identificar Pokémon** para comenzar.")
    st.stop()

ai = ai_result.get("ai", {})
match = ai_result.get("match")

# ---- mostrar info del modelo ----
st.subheader("🧠 Resultado de la IA")

st.markdown(
    f"""
    <div style="
        background: #eef6ff;
        padding: 1.2rem;
        border-left: 6px solid #4aa3ff;
        border-radius: 5px;
        margin-bottom: 1rem;
    ">
        <b>Pokémon detectado:</b> {ai.get('primary_name', '—')}<br>
        <b>Razonamiento:</b> {ai.get('rationale', '—')}
    </div>
    """,
    unsafe_allow_html=True,
)

# ---- candidatos ----
candidates = ai.get("candidates", [])
if candidates:
    st.markdown("### 📝 Otros posibles candidatos:")
    for c in candidates:
        # c puede ser dict (name, confidence) según tu DTO
        if isinstance(c, dict):
            name = c.get("name", "—")
            conf = c.get("confidence", None)
            if conf is not None:
                st.write(f"• {name} (confianza: {conf:.2f})")
            else:
                st.write(f"• {name}")
        else:
            st.write(f"• {c}")

st.markdown("---")

# ---- mostrar Pokémon final ----
if match:
    st.subheader("🎯 Coincidencia encontrada")
    pokemon_card(match)

    st.markdown("### ➕ Acciones")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("📦 Agregar a mi colección"):
            ok_add, resp_add = api_collection_add(st.session_state.access_token, match["id"])
            if ok_add:
                st.success("✅ Pokémon agregado a tu colección")
            else:
                st.error((resp_add or {}).get("detail", "❌ No se pudo agregar"))
        
else:
    st.warning("⚠ No se encontró coincidencia en la Pokédex. Intenta con otra imagen.")