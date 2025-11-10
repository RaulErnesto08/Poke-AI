# import streamlit as st
# from utils.ui import page_header, inject_global_css, pokemon_card, sidebar_auth_block
# from utils.api import api_pokedex_get, api_pokedex_random, api_pokedex_search, api_collection_add
# from utils.auth import require_auth, logout

# st.set_page_config(page_title="Pokédex", page_icon="📘", layout="wide")

# # ---- Requiere sesión ----
# require_auth()
# sidebar_auth_block(on_logout=logout)

# # ---- Estado ----
# if "pk_current" not in st.session_state:
#     st.session_state.pk_current = None
# if "pk_last_query" not in st.session_state:
#     st.session_state.pk_last_query = ""
# if "pk_browse_id" not in st.session_state:
#     st.session_state.pk_browse_id = 1
# if "pk_trigger_search" not in st.session_state:
#     st.session_state.pk_trigger_search = False
# if "pk_search_input" not in st.session_state:
#     st.session_state.pk_search_input = st.session_state.pk_last_query

# inject_global_css()
# page_header("📘 Pokédex", "Busca, explora y descubre Pokémon")

# tabs = st.tabs(["🔎 Buscar", "🎲 Random", "📚 Explorar"])

# # --------------------------------------------------------------------
# # TAB 1 — BUSCAR
# # --------------------------------------------------------------------
# with tabs[0]:
#     st.subheader("Buscar por nombre o ID")

#     # Si fue activada por sugerencia → búsqueda automática
#     if st.session_state.pk_trigger_search and st.session_state.pk_search_input.strip():
#         q0 = st.session_state.pk_search_input.strip()
#         ok0, data0 = api_pokedex_get(q0)
#         if ok0 and data0:
#             st.session_state.pk_current = data0
#             st.session_state.pk_browse_id = data0.get("id", st.session_state.pk_browse_id)
#             st.session_state.pk_last_query = q0
#         st.session_state.pk_trigger_search = False

#     # Input de búsqueda
#     q = st.text_input(
#         "Nombre o ID",
#         key="pk_search_input",
#         placeholder="pikachu, 25, char..."
#     )

#     col_a, col_b = st.columns([1, 1])

#     # Botón Buscar
#     with col_a:
#         if st.button("Buscar"):
#             if q.strip():
#                 ok, data = api_pokedex_get(q.strip())
#                 if ok and data:
#                     st.session_state.pk_current = data
#                     st.session_state.pk_browse_id = data.get("id", st.session_state.pk_browse_id)
#                     st.session_state.pk_last_query = q.strip()
#                 else:
#                     st.error("No se encontró el Pokémon.")
#             else:
#                 st.warning("Escribe algo para buscar.")

#     # Botón Sugerencias
#     with col_b:
#         suggest = st.button("Sugerencias (autocompletar)")

#     # Mostrar sugerencias debajo
#     if suggest and q.strip():
#         ok, items = api_pokedex_search(q.strip(), limit=12)
#         if ok and items:
#             st.caption("Sugerencias")
#             cols = st.columns(4)

#             for i, it in enumerate(items):
#                 name = it.get("name", "")
#                 pid = it.get("id")
#                 label = f"#{pid} {name}" if pid else name

#                 if cols[i % 4].button(label, key=f"sugg_{name}_{pid}_{i}"):
#                     st.session_state.pk_search_input = name
#                     st.session_state.pk_last_query = name
#                     st.session_state.pk_trigger_search = True
#                     st.rerun()

# # --------------------------------------------------------------------
# # TAB 2 — RANDOM
# # --------------------------------------------------------------------
# with tabs[1]:
#     st.subheader("¡Sorpresa!")
#     if st.button("🎁 Dame un Pokémon al azar"):
#         ok, data = api_pokedex_random()
#         if ok and data:
#             st.session_state.pk_current = data
#             st.session_state.pk_browse_id = data.get("id", st.session_state.pk_browse_id)

# # --------------------------------------------------------------------
# # TAB 3 — EXPLORAR (prev/next)
# # --------------------------------------------------------------------
# with tabs[2]:
#     st.subheader("Navegación por ID")

#     col1, col2, col3, col4 = st.columns([1, 1, 2, 2])

#     with col1:
#         if st.button("⬅️ Prev"):
#             st.session_state.pk_browse_id = max(1, int(st.session_state.pk_browse_id) - 1)
#             ok, data = api_pokedex_get(st.session_state.pk_browse_id)
#             if ok:
#                 st.session_state.pk_current = data

#     with col2:
#         if st.button("Next ➡️"):
#             st.session_state.pk_browse_id = int(st.session_state.pk_browse_id) + 1
#             ok, data = api_pokedex_get(st.session_state.pk_browse_id)
#             if ok:
#                 st.session_state.pk_current = data

#     with col3:
#         new_id = st.number_input(
#             "ID",
#             min_value=1,
#             max_value=20000,
#             value=int(st.session_state.pk_browse_id),
#             step=1,
#         )

#     with col4:
#         if st.button("Ir"):
#             st.session_state.pk_browse_id = int(new_id)
#             ok, data = api_pokedex_get(st.session_state.pk_browse_id)
#             if ok:
#                 st.session_state.pk_current = data

# # --------------------------------------------------------------------
# # RENDER DE LA TARJETA
# # --------------------------------------------------------------------
# st.markdown("---")
# if st.session_state.pk_current:
#     p = st.session_state.pk_current
#     pokemon_card(p)

#     # --- Añadir a colección ---
# from utils.api import api_collection_add, api_ai_fun_facts
# from utils.auth import is_authenticated

# if is_authenticated() and p.get("id"):
#     col1, col2 = st.columns(2)

#     # Botón para agregar
#     with col1:
#         if st.button("➕ Agregar a mi colección"):
#             ok, data = api_collection_add(st.session_state.access_token, int(p["id"]))
#             if ok:
#                 st.success("Agregado a tu colección ✅")
#             else:
#                 detail = (data or {}).get("detail", "No se pudo agregar")
#                 st.error(f"❌ {detail}")

#     # Botón Fun Facts
#     with col2:
#         if st.button("💡 Datos curiosos ✨"):
#             with st.spinner("Consultando a la IA..."):
#                 ok_fun, fun = api_ai_fun_facts(st.session_state.access_token, int(p["id"]))

#                 if ok_fun:
#                     facts = fun.get("fun_facts", [])

#                     if isinstance(facts, list) and facts:
#                         st.markdown("### 💡 Datos Curiosos ✨")

#                         for item in facts:
#                             fact = item.get("fact", "")
#                             relevance = item.get("relevance", "")

#                             st.markdown(
#                                 f"""
#                                 <div style="
#                                     padding:0.6rem;
#                                     margin-bottom:0.5rem;
#                                     border-radius:8px;
#                                     background:#fafafa;
#                                     border:1px solid #eee;
#                                 ">
#                                     <strong>📌 {fact}</strong><br/>
#                                     <span style="color:#555;">{relevance}</span>
#                                 </div>
#                                 """,
#                                 unsafe_allow_html=True
#                             )
#                     else:
#                         st.info("No se encontraron datos curiosos.")
                    
#                 else:
#                     detail = (fun or {}).get("detail", "No se pudo obtener información")
#                     st.error(f"❌ {detail}")
# else:
#     st.info("Usa **Buscar**, **Random**, o **Explorar** para ver un Pokémon.")

import streamlit as st
from utils.ui import page_header, inject_global_css, pokemon_card, sidebar_auth_block
from utils.api import (
    api_pokedex_get,
    api_pokedex_random,
    api_pokedex_search,
    api_collection_add,
    api_ai_fun_facts
)
from utils.auth import require_auth, logout, is_authenticated

# --------------------------------------------------------------------
# CONFIGURACIÓN
# --------------------------------------------------------------------
st.set_page_config(page_title="Pokédex", page_icon="📘", layout="wide")

require_auth()
sidebar_auth_block(on_logout=logout)
inject_global_css()

page_header("📘 Pokédex", "Busca, explora y descubre Pokémon")

# --------------------------------------------------------------------
# ESTADO
# --------------------------------------------------------------------
st.session_state.setdefault("pk_current", None)
st.session_state.setdefault("pk_last_query", "")
st.session_state.setdefault("pk_browse_id", 1)
st.session_state.setdefault("pk_trigger_search", False)
st.session_state.setdefault("pk_search_input", "")


# --------------------------------------------------------------------
# TAB OBJETOS
# --------------------------------------------------------------------
tab_search, tab_random, tab_browse = st.tabs(["🔎 Buscar", "🎲 Random", "📚 Explorar"])

# --------------------------------------------------------------------
# TAB: BUSCAR
# --------------------------------------------------------------------
with tab_search:
    st.subheader("Buscar por nombre o ID")

    # Si viene de sugerencias, ejecutar búsqueda automática
    if st.session_state.pk_trigger_search and st.session_state.pk_search_input.strip():
        q_auto = st.session_state.pk_search_input.strip()
        ok_auto, data_auto = api_pokedex_get(q_auto)
        if ok_auto and data_auto:
            st.session_state.pk_current = data_auto
            st.session_state.pk_browse_id = data_auto.get("id", st.session_state.pk_browse_id)
        st.session_state.pk_trigger_search = False

    # Campo de búsqueda
    q = st.text_input(
        "Nombre o ID",
        key="pk_search_input",
        placeholder="pikachu, 25, char..."
    )

    col_a, col_b = st.columns(2)

    # Botón Buscar
    with col_a:
        if st.button("Buscar"):
            query = q.strip()
            if query:
                ok, data = api_pokedex_get(query)
                if ok and data:
                    st.session_state.pk_current = data
                    st.session_state.pk_browse_id = data.get("id", st.session_state.pk_browse_id)
                else:
                    st.error("No se encontró el Pokémon.")
            else:
                st.warning("Escribe un nombre o ID.")

    # Botón Sugerencias
    with col_b:
        suggest = st.button("Sugerencias (autocompletar)")

    if suggest and q.strip():
        ok_s, items = api_pokedex_search(q.strip(), limit=12)
        if ok_s and items:
            st.caption("Sugerencias")
            cols = st.columns(4)

            for i, it in enumerate(items):
                name = it.get("name", "")
                pid = it.get("id")
                label = f"#{pid} {name}" if pid else name

                # Botón sugerencia
                if cols[i % 4].button(label, key=f"sugg_{name}_{pid}_{i}"):
                    st.session_state.pk_search_input = name
                    st.session_state.pk_last_query = name
                    st.session_state.pk_trigger_search = True
                    st.rerun()

# --------------------------------------------------------------------
# TAB: RANDOM
# --------------------------------------------------------------------
with tab_random:
    st.subheader("¡Sorpresa!")
    if st.button("🎁 Dame un Pokémon al azar"):
        ok_r, data_r = api_pokedex_random()
        if ok_r:
            st.session_state.pk_current = data_r
            st.session_state.pk_browse_id = data_r.get("id", st.session_state.pk_browse_id)

# --------------------------------------------------------------------
# TAB: BROWSE
# --------------------------------------------------------------------
with tab_browse:
    st.subheader("Navegación por ID")

    col1, col2, col3, col4 = st.columns([1, 1, 2, 2])

    with col1:
        if st.button("⬅️ Prev"):
            st.session_state.pk_browse_id = max(1, st.session_state.pk_browse_id - 1)
            ok_p, data_p = api_pokedex_get(st.session_state.pk_browse_id)
            if ok_p:
                st.session_state.pk_current = data_p

    with col2:
        if st.button("Next ➡️"):
            st.session_state.pk_browse_id += 1
            ok_n, data_n = api_pokedex_get(st.session_state.pk_browse_id)
            if ok_n:
                st.session_state.pk_current = data_n

    with col3:
        new_id = st.number_input(
            "ID",
            min_value=1,
            max_value=20000,
            value=st.session_state.pk_browse_id,
            step=1,
        )

    with col4:
        if st.button("Ir"):
            st.session_state.pk_browse_id = int(new_id)
            ok_i, data_i = api_pokedex_get(st.session_state.pk_browse_id)
            if ok_i:
                st.session_state.pk_current = data_i


# --------------------------------------------------------------------
# RENDER DE TARJETA + ACCIONES
# --------------------------------------------------------------------
st.markdown("---")

p = st.session_state.pk_current

if p:
    pokemon_card(p)

    if is_authenticated():
        col1, col2 = st.columns(2)

        # Botón agregar a colección
        with col1:
            if st.button("➕ Agregar a mi colección"):
                ok_c, resp_c = api_collection_add(st.session_state.access_token, p["id"])
                if ok_c:
                    st.success("Agregado a tu colección ✅")
                else:
                    st.error(resp_c.get("detail", "No se pudo agregar"))

        # Botón datos curiosos
        with col2:
            if st.button("💡 Datos curiosos ✨"):
                with st.spinner("Consultando a la IA..."):
                    ok_f, resp_f = api_ai_fun_facts(st.session_state.access_token, p["id"])
                    if ok_f:
                        facts = resp_f.get("fun_facts", [])
                        st.markdown("### 💡 Datos Curiosos ✨")

                        for fitem in facts:
                            st.markdown(
                                f"""
                                <div style="
                                    background:#fafafa;
                                    border:1px solid #eee;
                                    padding:0.8rem;
                                    border-radius:8px;
                                    margin-bottom:0.6rem;
                                ">
                                    <strong>📌 {fitem.get('fact','')}</strong><br>
                                    <span style='color:#555'>{fitem.get('relevance','')}</span>
                                </div>
                                """,
                                unsafe_allow_html=True
                            )
                    else:
                        st.error(resp_f.get("detail", "Error al obtener datos curiosos"))
else:
    st.info("Usa **Buscar**, **Random**, o **Explorar** para ver un Pokémon.")