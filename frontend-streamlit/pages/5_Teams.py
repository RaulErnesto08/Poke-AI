# pages/6_Teams.py
import streamlit as st
from utils.ui import page_header, inject_global_css, sidebar_auth_block
from utils.auth import require_auth, logout
from utils.api import (
    api_teams_get,
    api_team_create,
    api_team_delete,
    api_team_update_name,
    api_team_get_members,
    api_team_remove_member,
    api_team_add_member,
    api_ai_auto_team,  # <- NUEVO: endpoint de Auto Team Builder (POST /ai/auto-team)
)

st.set_page_config(page_title="Teams", page_icon="🧩", layout="wide")
require_auth()
sidebar_auth_block(on_logout=logout)
inject_global_css()

page_header("🧩 Teams", "Organiza tus Pokémon en equipos")

# Estado global
if "team_selected" not in st.session_state:
    st.session_state.team_selected = None
if "auto_team_cache" not in st.session_state:
    st.session_state.auto_team_cache = None

# -----------------------------------------
# Render: Vista de un Team seleccionado
# -----------------------------------------
def render_view(team_id: int):
    st.markdown("### 👁️ Detalles del equipo")
    ok, team_info = api_team_get_members(st.session_state.access_token, team_id)

    if not ok:
        st.error("No se pudo cargar el equipo.")
        return

    st.write(f"Equipo: **{team_info['name']}**")
    st.write(f"Miembros: **{team_info['count']}/6**")

    # Renombrar
    new_name = st.text_input("Renombrar Team", value=team_info["name"], key=f"rename_input_{team_id}")
    if st.button("Guardar nombre", key=f"save_name_{team_id}"):
        ok_rename, resp = api_team_update_name(st.session_state.access_token, team_id, new_name.strip())
        if ok_rename:
            st.success("Nombre actualizado ✅")
            st.rerun()
        else:
            st.error((resp or {}).get("detail", "No se pudo renombrar el equipo."))

    st.markdown("---")

    st.markdown("### 🧩 Miembros del equipo")

    if team_info["members"]:
        cols = st.columns(3)
        for i, m in enumerate(team_info["members"]):
            with cols[i % 3]:
                st.markdown(
                    f"""
                    <div style="
                        padding: 1rem;
                        border-radius: 10px;
                        background: #ffffff;
                        margin-bottom: 1rem;
                        text-align:center;
                        box-shadow:0 0 4px rgba(0,0,0,0.1);
                    ">
                        <h4>#{m['id']} {m['name']}</h4>
                        <img src="{m['sprite']}" width="96" />
                    </div>
                """,
                    unsafe_allow_html=True,
                )
                if st.button("Quitar", key=f"rm_{team_id}_{m['id']}"):
                    ok_rm, msg = api_team_remove_member(
                        st.session_state.access_token, team_id, m["id"]
                    )
                    if ok_rm:
                        st.success("Eliminado ✅")
                        st.rerun()
                    else:
                        st.error((msg or {}).get("detail", "No se pudo quitar el Pokémon"))
    else:
        st.info("Este equipo todavía no tiene miembros.")

    st.markdown("---")


# -----------------------------------------
# Helpers: UI de Team list con conteos
# -----------------------------------------
def team_display_label(t: dict) -> str:
    count = t.get("count", 0)
    label = f"{t['name']} ({count}/6)"
    if count >= 6:
        label += " — lleno"
    return label


# -----------------------------------------
# UI con Tabs (List, Crear, Auto Builder)
# -----------------------------------------
tab_list, tab_create, tab_auto = st.tabs(["📄 Mis Teams", "➕ Crear Team", "🤖 Auto Team Builder"])

# ===========================
# TAB 1: Mis Teams
# ===========================
with tab_list:
    st.subheader("📄 Tus equipos")

    ok, teams = api_teams_get(st.session_state.access_token)

    if not ok:
        st.error("No se pudieron cargar tus equipos.")
    else:
        if not teams:
            st.info("Todavía no tienes equipos creados.")
        else:
            cols = st.columns(3)
            for i, t in enumerate(teams):
                with cols[i % 3]:
                    st.markdown(
                        f"""
                        <div style="
                            padding:1rem;
                            border-radius:10px;
                            background:#f5f5f5;
                            margin-bottom:1rem;
                            box-shadow:0 0 4px rgba(0,0,0,0.1);
                        ">
                            <h3>⭐ {t['name']}</h3>
                            <p>🧿 {t['count']} Pokémon</p>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                    colA, colB = st.columns(2)

                    with colA:
                        if st.button("🔎 Ver", key=f"view_{t['id']}"):
                            st.session_state.team_selected = t["id"]
                            st.rerun()

                    with colB:
                        if st.button("❌ Borrar", key=f"del_{t['id']}"):
                            ok_del, msg_del = api_team_delete(st.session_state.access_token, t["id"])
                            if ok_del:
                                st.success("Team eliminado ✅")
                                st.rerun()
                            else:
                                st.error((msg_del or {}).get("detail", "No se pudo borrar el Team"))

    # Mostrar el team seleccionado debajo
    if st.session_state.team_selected:
        st.markdown("---")
        render_view(st.session_state.team_selected)

# ===========================
# TAB 2: Crear Team
# ===========================
with tab_create:
    st.subheader("➕ Crear nuevo equipo")
    with st.form("create_team_form"):
        name = st.text_input("Nombre del Team", placeholder="Ej: Legends")
        submitted = st.form_submit_button("Crear Team")

    if submitted:
        if name.strip():
            ok_create, detail = api_team_create(st.session_state.access_token, name.strip())
            if ok_create:
                st.success("Team creado ✅")
                st.session_state.team_selected = detail.get("id")
                st.rerun()
            else:
                st.error((detail or {}).get("detail", "Error al crear el Team"))
        else:
            st.warning("El nombre no puede estar vacío.")

# ===========================
# TAB 3: Auto Team Builder
# ===========================
with tab_auto:
    st.subheader("🤖 Construcción automática de equipo")
    st.caption(
        "La IA analiza tu colección y sugiere un equipo balanceado (hasta 6). "
        "Puedes crear un Team nuevo con la sugerencia o aplicar los miembros a un Team existente."
    )

    # Acciones: generar / regenerar
    colg1, colg2 = st.columns([1, 1])
    with colg1:
        generate = st.button("✨ Generar equipo sugerido")
    with colg2:
        regen = st.button("🔄 Regenerar")

    if generate or regen or (st.session_state.auto_team_cache is None):
        with st.spinner("Pensando un equipo óptimo para tu colección..."):
            ok_auto, data_auto = api_ai_auto_team(st.session_state.access_token)
        if not ok_auto:
            st.error((data_auto or {}).get("detail", "No se pudo generar el equipo"))
            st.stop()
        st.session_state.auto_team_cache = data_auto

    suggestion = st.session_state.auto_team_cache or {}
    if not suggestion:
        st.info("Aún no hay sugerencias. Da clic en **Generar equipo sugerido**.")
        st.stop()

    # Resumen IA
    st.markdown("### 🧠 Análisis")
    st.markdown(suggestion.get("summary", "Sin resumen"))

    members = suggestion.get("team", []) or []

    if not members:
        st.warning("No recibimos miembros sugeridos.")
        st.stop()

    st.markdown("---")
    st.markdown("### 🧩 Miembros sugeridos")

    grid = st.columns(3)
    for i, m in enumerate(members):
        with grid[i % 3]:
            # Seguridad: algunos modelos pueden enviar campos faltantes
            pid = m.get("id")
            name = (m.get("name") or "").capitalize()
            sprite = m.get("sprite")
            types = ", ".join(m.get("types") or [])
            reason = m.get("reason", "")

            st.markdown(
                f"""
                <div style="
                    padding: 1rem;
                    border-radius: 12px;
                    background: #fff;
                    margin-bottom: 1rem;
                    box-shadow: 0 0 8px rgba(0,0,0,0.08);
                ">
                    <div style="display:flex; align-items:center; gap:.75rem;">
                        <img src="{sprite}" width="72">
                        <div>
                            <h4 style="margin:0;">#{pid or '—'} {name}</h4>
                            <div style="opacity:.8;">Tipos: {types or '—'}</div>
                        </div>
                    </div>
                    <div style="margin-top:.5rem; font-size:.9rem; opacity:.9;">
                        {reason}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown("---")

    # Aplicar a Team existente
    st.markdown("#### ➕ Agregar estos 6 a un Team existente")
    ok_list, teams_for_apply = api_teams_get(st.session_state.access_token)
    if ok_list and teams_for_apply:
        # Build labels con conteo
        labels = [team_display_label(t) for t in teams_for_apply]
        choice = st.selectbox("Selecciona un Team", options=labels, key="auto_apply_select")

        selected_idx = labels.index(choice)
        chosen_team = teams_for_apply[selected_idx]
        is_full = chosen_team.get("count", 0) >= 6

        if is_full:
            st.warning(f"El equipo **{chosen_team['name']}** ya está lleno (6/6).")
        else:
            if st.button("👉 Agregar todos al Team seleccionado"):
                successes, conflicts, errors = 0, 0, 0
                for m in members:
                    pid = m.get("id")
                    if not pid:
                        errors += 1
                        continue
                    ok_add, resp = api_team_add_member(st.session_state.access_token, chosen_team["id"], int(pid))
                    if ok_add:
                        successes += 1
                    else:
                        # 409 duplicado o 400/otros
                        detail = (resp or {}).get("detail", "")
                        if "already" in detail.lower():
                            conflicts += 1
                        else:
                            errors += 1
                st.success(f"Listo: añadidos {successes}, duplicados {conflicts}, errores {errors}.")
                st.session_state.team_selected = chosen_team["id"]
                st.rerun()
    else:
        st.info("Crea un Team primero para poder aplicar la sugerencia aquí.")

    st.markdown("---")

    # Crear Team nuevo con los 6
    st.markdown("#### 🆕 Crear un nuevo Team con estos 6")
    new_name = st.text_input("Nombre del nuevo Team", value="AI Squad")
    if st.button("🚀 Crear Team y agregar miembros"):
        if not new_name.strip():
            st.warning("El nombre no puede estar vacío.")
        else:
            ok_new, detail_new = api_team_create(st.session_state.access_token, new_name.strip())
            if not ok_new:
                st.error((detail_new or {}).get("detail", "No se pudo crear el Team"))
            else:
                new_team_id = detail_new.get("id")
                successes, conflicts, errors = 0, 0, 0
                for m in members:
                    pid = m.get("id")
                    if not pid:
                        errors += 1
                        continue
                    ok_add, resp = api_team_add_member(st.session_state.access_token, new_team_id, int(pid))
                    if ok_add:
                        successes += 1
                    else:
                        detail = (resp or {}).get("detail", "")
                        if "already" in detail.lower():
                            conflicts += 1
                        else:
                            errors += 1
                st.success(f"Team **{new_name}** creado ✅ | añadidos {successes}, duplicados {conflicts}, errores {errors}.")
                st.session_state.team_selected = new_team_id
                st.rerun()