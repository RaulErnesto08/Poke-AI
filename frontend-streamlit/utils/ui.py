import streamlit as st
from typing import Iterable

# Paleta por tipo (simple y limpia)
TYPE_COLORS = {
    "normal": "#A8A77A", "fire": "#EE8130", "water": "#6390F0", "electric": "#F7D02C",
    "grass": "#7AC74C", "ice": "#96D9D6", "fighting": "#C22E28", "poison": "#A33EA1",
    "ground": "#E2BF65", "flying": "#A98FF3", "psychic": "#F95587", "bug": "#A6B91A",
    "rock": "#B6A136", "ghost": "#735797", "dragon": "#6F35FC", "dark": "#705746",
    "steel": "#B7B7CE", "fairy": "#D685AD",
}

BASE_STAT_MAX = 255  # escala aproximada

GLOBAL_CSS = """
<style>
.badge {
  display:inline-block;
  padding: 4px 10px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 600;
  color: white;
  margin-right: 6px;
}
.stat-row {
  display:flex;
  align-items:center;
  gap:10px;
  margin-bottom:8px;
}
.stat-name {
  width: 70px;
  text-transform: uppercase;
  font-weight: 700;
  font-size: 12px;
  opacity: 0.75;
}
.stat-bar {
  height: 10px;
  background: #e6e6e6;
  border-radius: 8px;
  width: 100%;
  overflow: hidden;
}
.stat-fill {
  height: 10px;
  border-radius: 8px;
  background: linear-gradient(90deg, #7c4dff, #00d4ff);
}
.card {
  background: white;
  padding: 18px;
  border-radius: 16px;
  box-shadow: 0 8px 26px rgba(0,0,0,0.06);
  border: 1px solid rgba(0,0,0,0.05);
}
img.sprite {
  image-rendering: pixelated;
  width: 180px;
}
.search-chip {
  display:inline-block;
  padding:6px 10px;
  border-radius: 8px;
  border: 1px solid #e7e7e7;
  background: #fafafa;
  margin: 4px 6px 0 0;
  cursor: pointer;
  font-size: 13px;
}
</style>
"""

def inject_global_css():
    st.markdown(GLOBAL_CSS, unsafe_allow_html=True)

def page_header(title: str, subtitle: str | None = None):
    st.title(title)
    if subtitle:
        st.caption(subtitle)

def sidebar_auth_block(on_logout):
    with st.sidebar:
        st.markdown("### Session")
        st.button("Logout", on_click=on_logout)

def type_badges(types: Iterable[str]):
    spans = []
    for t in types:
        color = TYPE_COLORS.get(t, "#888888")
        spans.append(f'<span class="badge" style="background:{color}">{t}</span>')
    st.markdown(" ".join(spans), unsafe_allow_html=True)

def stat_row(name: str, value: int):
    pct = max(0, min(100, int(value * 100 / BASE_STAT_MAX)))
    st.markdown(
        f"""
        <div class="stat-row">
          <div class="stat-name">{name}</div>
          <div class="stat-bar">
            <div class="stat-fill" style="width:{pct}%"></div>
          </div>
          <div style="width:40px;text-align:right;font-weight:700;">{value}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

def pokemon_card(p: dict):
    """
    p = { id, name, sprite, types[], stats{ hp, attack, defense, sp_atk, sp_def, speed } }
    """
    with st.container():
        st.markdown('<div class="card">', unsafe_allow_html=True)
        c1, c2 = st.columns([1,2])
        with c1:
            if p.get("sprite"):
                st.markdown(f'<img class="sprite" src="{p["sprite"]}"/>', unsafe_allow_html=True)
            st.markdown(f"**#{p['id']:03d} — {p['name'].title()}**")
            type_badges(p.get("types", []))
        with c2:
            st.markdown("**Base Stats**")
            s = p.get("stats", {})
            stat_row("HP", s.get("hp", 0))
            stat_row("ATK", s.get("attack", 0))
            stat_row("DEF", s.get("defense", 0))
            stat_row("SpA", s.get("special_attack", 0))
            stat_row("SpD", s.get("special_defense", 0))
            stat_row("SPD", s.get("speed", 0))
        st.markdown('</div>', unsafe_allow_html=True)