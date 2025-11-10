import streamlit as st
from utils.auth import require_auth, logout, is_authenticated
from utils.ui import page_header, inject_global_css, pokemon_card, sidebar_auth_block
from utils.api import (
    api_collection_list,
    api_collection_add,
    api_pokedex_get,
    api_collection_remove,
    api_ai_recommendations, 
    api_teams_get,
    api_team_add_member
)

st.set_page_config(page_title="Mi colección", page_icon="📦", layout="wide")
require_auth()
sidebar_auth_block(on_logout=logout)
inject_global_css()

# Title
page_header("📦 Mi colección", "Tus Pokémon guardados y recomendaciones inteligentes")

# Load collection
ok, ids = api_collection_list(st.session_state.access_token)
if not ok:
    st.error("No se pudo cargar tu colección.")
    st.stop()

tabs = st.tabs(["📚 Mi colección", "✨ Recomendaciones"])

# ─────────────────────────────────────────
# TAB 1 – Mi colección
# ─────────────────────────────────────────
with tabs[0]:
    # Refresh automático si venimos desde recomendaciones
    if st.session_state.get("_refresh_collection"):
        del st.session_state["_refresh_collection"]
        st.rerun()
        
    if not ids:
        st.info("Aún no tienes Pokémon en tu colección. Ve a la Pokédex y agrega algunos.")
    else:
        st.subheader("📁 Pokémon guardados")
        st.markdown("Aquí puedes ver todos los Pokémon que has guardado en tu colección, administrarlos y eliminarlos si lo deseas.")

        cols = st.columns(2)
        for i, pid in enumerate(ids):
            col = cols[i % 2]
            with col:
                ok_p, p = api_pokedex_get(pid)
                if ok_p:
                    pokemon_card(p)

                    remove_key = f"remove_{pid}_{i}"
                    if st.button(f"❌ Quitar #{pid}", key=remove_key):
                        ok_rm, data = api_collection_remove(st.session_state.access_token, int(pid))
                        if ok_rm:
                            st.success("Eliminado ✅")
                            st.rerun()
                        else:
                            st.error((data or {}).get("detail", "No se pudo eliminar"))
                    # --- Agregar a un Team ---
                    ok_t, teams = api_teams_get(st.session_state.access_token)
                    if ok_t and teams:

                        # build display entries: "TeamName (X/6)" and detect full ones
                        display_names = []
                        for t in teams:
                            count = t.get("count", 0)
                            max_size = 6
                            display_label = f"{t['name']} ({count}/{max_size})"
                            if count >= max_size:
                                display_label += " — lleno"
                            display_names.append(display_label)

                        selected_display = st.selectbox(
                            "Agregar a Team:",
                            display_names,
                            key=f"team_select_{pid}_{i}"
                        )

                        # resolve the real team object
                        idx = display_names.index(selected_display)
                        team_obj = teams[idx]

                        # if team is full, disable adding
                        is_full = team_obj.get("count", 0) >= 6

                        if is_full:
                            st.warning(f"El equipo {team_obj['name']} está lleno (6/6).")
                        else:
                            if st.button(f"➕ Agregar a {team_obj['name']}", key=f"add_to_team_{pid}_{i}"):
                                ok_add, resp = api_team_add_member(
                                    st.session_state.access_token, team_obj["id"], pid
                                )

                                if ok_add:
                                    st.success(f"Añadido a {team_obj['name']} ✅")
                                else:
                                    detail = (resp or {}).get("detail", "No se pudo agregar al Team")
                                    st.error(f"❌ {detail}")
                else:
                    st.warning(f"No pude obtener detalles de Pokémon #{pid}")

# ─────────────────────────────────────────
# TAB 2 – Recomendaciones IA
# ─────────────────────────────────────────
with tabs[1]:

    st.subheader("✨ Recomendaciones personalizadas")

    st.markdown("""
    La IA analiza tu colección actual para sugerirte Pokémon que:
    - Complementan tus tipos
    - Cubren debilidades
    - Mejoran la sinergia del equipo
    """)

    if not ids:
        st.info("Necesitas tener Pokémon en tu colección para recibir recomendaciones.")
        st.stop()

    refresh = st.button("🔄 Volver a generar recomendaciones")

    if "recommendations_cache" not in st.session_state or refresh:
        with st.spinner("Analizando tu colección con IA..."):
            ok_rec, rec_data = api_ai_recommendations(st.session_state.access_token)
            if not ok_rec:
                st.error(rec_data.get("detail", "No se pudieron obtener recomendaciones"))
            else:
                st.session_state.recommendations_cache = rec_data

    rec_data = st.session_state.get("recommendations_cache", {})

    if rec_data:

        st.markdown(f"### 🧠 Análisis general\n{rec_data['summary']}")

        st.markdown("---")
        st.markdown("### 🎯 Pokémon recomendados")

        recs = rec_data["recommendations"]
        cols = st.columns(2)

        invalid_count = 0

        cols = st.columns(2)
        for i, r in enumerate(recs):

            # skip invalid recommendations
            if not r.get("id") or not r.get("sprite") or not r.get("name"):
                invalid_count += 1
                continue

            col = cols[i % 2]
            with col:
                st.markdown(f"### {r['name'].capitalize()}")

                # Pokémon image
                st.image(r["sprite"], width=120)

                # Types
                st.markdown(f"**Tipos:** {', '.join(r['types'])}")

                # AI reasoning
                st.markdown(f"**Por qué añadirlo:** {r['reason']}")

                # ---- ADD TO COLLECTION BUTTON ----
                if is_authenticated():
                    if st.button(f"➕ Agregar {r['name'].capitalize()} a mi colección", key=f"add_rec_{r['id']}"):
                        ok_add, resp = api_collection_add(st.session_state.access_token, int(r["id"]))
                        if ok_add:
                            st.success(f"{r['name'].capitalize()} añadido ✅")
                            st.session_state["_refresh_collection"] = True
                        else:
                            detail = (resp or {}).get("detail", "No se pudo agregar")
                            st.error(f"❌ {detail}")

                st.markdown("---")

        # feedback for invalids
        if invalid_count:
            st.info(f"⚠ La IA sugirió {invalid_count} Pokémon que no existen o no están en la PokeAPI. Fueron omitidos.")