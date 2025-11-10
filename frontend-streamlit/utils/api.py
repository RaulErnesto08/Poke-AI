import os
import requests
from dotenv import load_dotenv

load_dotenv()
API_URL = os.getenv("API_URL", "http://127.0.0.1:8000")

def _headers(token: str | None = None) -> dict:
    h = {"Content-Type": "application/json"}
    if token:
        h["Authorization"] = f"Bearer {token}"
    return h

# -------- Auth --------
def api_login(email: str, password: str) -> tuple[bool, dict | None]:
    url = f"{API_URL}/auth/login"
    r = requests.post(url, json={"email": email, "password": password}, timeout=15)
    if r.status_code == 200:
        return True, r.json()
    return False, r.json() if r.headers.get("content-type","").startswith("application/json") else {"detail": r.text}

def api_register(email: str, password: str) -> tuple[bool, dict | None]:
    url = f"{API_URL}/auth/register"
    r = requests.post(url, json={"email": email, "password": password}, timeout=15)
    if r.status_code in (200, 201):
        return True, r.json()
    return False, r.json() if r.headers.get("content-type","").startswith("application/json") else {"detail": r.text}

def api_me(access_token: str) -> tuple[bool, dict | None]:
    url = f"{API_URL}/auth/me"
    r = requests.get(url, headers=_headers(access_token), timeout=15)
    if r.status_code == 200:
        return True, r.json()
    return False, None

def api_refresh_with_access(access_token: str) -> tuple[bool, dict | None]:
    """
    ⚠️ Usa el flujo actual de tu backend: refresh con Access Token válido.
    """
    url = f"{API_URL}/auth/refresh"
    r = requests.post(url, headers=_headers(access_token), timeout=15)
    if r.status_code == 200:
        return True, r.json()
    return False, r.json() if r.headers.get("content-type","").startswith("application/json") else {"detail": r.text}

# -------- Pokedex --------
def api_pokedex_get(id_or_name: str | int) -> tuple[bool, dict | None]:
    url = f"{API_URL}/pokedex/look/{id_or_name}"
    r = requests.get(url, timeout=15)
    if r.status_code == 200:
        return True, r.json()
    return False, r.json() if r.headers.get("content-type","").startswith("application/json") else {"detail": r.text}

def api_pokedex_random() -> tuple[bool, dict | None]:
    url = f"{API_URL}/pokedex/random"
    r = requests.get(url, timeout=15)
    if r.status_code == 200:
        return True, r.json()
    return False, r.json() if r.headers.get("content-type","").startswith("application/json") else {"detail": r.text}

def api_pokedex_search(query: str, limit: int = 12) -> tuple[bool, list[dict]]:
    url = f"{API_URL}/pokedex/search"
    r = requests.get(url, params={"query": query, "limit": limit}, timeout=15)
    if r.status_code == 200:
        data = r.json() or {}
        return True, data.get("items", [])
    return False, []

def api_ai_fun_facts(access_token: str, pokemon_id: int) -> tuple[bool, dict]:
    url = f"{API_URL}/ai/fun-facts/{pokemon_id}"
    r = requests.get(url, headers=_headers(access_token), timeout=30)

    if r.status_code == 200:
        return True, r.json()

    try:
        return False, r.json()
    except:
        return False, {"detail": r.text}

# --- Collection (requires Authorization) ---
def api_collection_list(access_token: str) -> tuple[bool, list[int]]:
    url = f"{API_URL}/collection"
    r = requests.get(url, headers=_headers(access_token), timeout=15)
    if r.status_code == 200:
        return True, (r.json() or {}).get("items", [])
    return False, []

def api_collection_add(access_token: str, pokemon_id: int) -> tuple[bool, dict | None]:
    url = f"{API_URL}/collection/add/{pokemon_id}"
    r = requests.post(url, headers=_headers(access_token), timeout=15)
    if r.status_code in (200, 201):
        return True, r.json()
    return False, r.json() if r.headers.get("content-type","").startswith("application/json") else {"detail": r.text}

def api_collection_remove(access_token: str, pokemon_id: int) -> tuple[bool, dict | None]:
    url = f"{API_URL}/collection/remove/{pokemon_id}"
    r = requests.delete(url, headers=_headers(access_token), timeout=15)
    if r.status_code == 200:
        return True, r.json()
    return False, r.json() if r.headers.get("content-type","").startswith("application/json") else {"detail": r.text}

def api_ai_recommendations(access_token: str) -> tuple[bool, dict]:
    url = f"{API_URL}/ai/recommendations"
    r = requests.post(url, headers=_headers(access_token), timeout=30)

    if r.status_code == 200:
        return True, r.json()

    return False, r.json() if r.headers.get("content-type", "").startswith("application/json") else {"detail": r.text}

# ---- Teams (requires Authorization) ----

def api_teams_get(access_token: str) -> tuple[bool, list[dict]]:
    """GET /teams -> lista de teams con counts"""
    url = f"{API_URL}/teams"
    r = requests.get(url, headers=_headers(access_token), timeout=15)

    if r.status_code == 200:
        return True, r.json() or []

    try:
        return False, r.json()
    except:
        return False, {"detail": r.text}


def api_team_create(access_token: str, name: str) -> tuple[bool, dict]:
    """POST /teams -> crear un Team (devuelve TeamDetail)"""
    url = f"{API_URL}/teams"
    r = requests.post(
        url,
        json={"name": name},
        headers=_headers(access_token),
        timeout=15,
    )

    if r.status_code in (200, 201):
        return True, r.json()

    try:
        return False, r.json()
    except:
        return False, {"detail": r.text}


def api_team_delete(access_token: str, team_id: int) -> tuple[bool, dict]:
    """DELETE /teams/{team_id} -> eliminar team"""
    url = f"{API_URL}/teams/{team_id}"
    r = requests.delete(url, headers=_headers(access_token), timeout=15)

    if r.status_code == 200:
        return True, r.json()

    try:
        return False, r.json()
    except:
        return False, {"detail": r.text}


def api_team_get_members(access_token: str, team_id: int) -> tuple[bool, dict]:
    """GET /teams/{team_id} -> obtener TeamDetail"""
    url = f"{API_URL}/teams/{team_id}"
    r = requests.get(url, headers=_headers(access_token), timeout=15)

    if r.status_code == 200:
        return True, r.json()

    try:
        return False, r.json()
    except:
        return False, {"detail": r.text}


def api_team_update_name(access_token: str, team_id: int, new_name: str) -> tuple[bool, dict]:
    """PATCH /teams/{team_id}/rename -> renombrar Team y devolver TeamDetail"""
    url = f"{API_URL}/teams/{team_id}/rename"
    r = requests.patch(
        url,
        json={"new_name": new_name},
        headers=_headers(access_token),
        timeout=15,
    )

    if r.status_code == 200:
        return True, r.json()

    try:
        return False, r.json()
    except:
        return False, {"detail": r.text}


def api_team_add_member(access_token: str, team_id: int, pokemon_id: int) -> tuple[bool, dict]:
    """POST /teams/{team_id}/add/{pokemon_id} -> agregar miembro y devolver TeamDetail"""
    url = f"{API_URL}/teams/{team_id}/add/{pokemon_id}"
    r = requests.post(url, headers=_headers(access_token), timeout=15)

    if r.status_code in (200, 201):
        return True, r.json()

    try:
        return False, r.json()
    except:
        return False, {"detail": r.text}


def api_team_remove_member(access_token: str, team_id: int, pokemon_id: int) -> tuple[bool, dict]:
    """DELETE /teams/{team_id}/remove/{pokemon_id} -> quitar miembro y devolver TeamDetail"""
    url = f"{API_URL}/teams/{team_id}/remove/{pokemon_id}"
    r = requests.delete(url, headers=_headers(access_token), timeout=15)

    if r.status_code == 200:
        return True, r.json()

    try:
        return False, r.json()
    except:
        return False, {"detail": r.text}
    
def api_ai_auto_team(access_token: str) -> tuple[bool, dict]:
    """POST /ai/auto-team -> genera un equipo sugerido con IA"""
    url = f"{API_URL}/ai/auto-team"
    r = requests.post(url, headers=_headers(access_token), timeout=60)

    if r.status_code == 200:
        return True, r.json()

    try:
        return False, r.json()
    except:
        return False, {"detail": r.text}
    
# ---- AI Vision (requires Authorization) ----
def api_ai_identify(access_token: str, uploaded_file) -> tuple[bool, dict | None]:
    """
    POST /ai/identify -> identificar Pokémon desde imagen
    - uploaded_file: Streamlit UploadedFile
    """
    url = f"{API_URL}/ai/identify"
    
    headers = {"Authorization": f"Bearer {access_token}"}

    # Streamlit UploadedFile -> tuple (filename, bytes, content_type)
    filename = getattr(uploaded_file, "name", "image.jpg")
    content_type = getattr(uploaded_file, "type", None) or "application/octet-stream"
    file_bytes = uploaded_file.getvalue()
    files = {"image": (filename, file_bytes, content_type)}

    r = requests.post(url, headers=headers, files=files, timeout=30)

    if r.status_code == 200:
        return True, r.json()
    return False, (
        r.json() if r.headers.get("content-type", "").startswith("application/json")
        else {"detail": r.text}
    )
    
# ---- AI Compare ----

def api_ai_compare(pokemon_a: str | int, pokemon_b: str | int, access_token: str) -> tuple[bool, dict]:
    url = f"{API_URL}/ai/compare"
    payload = {
        "pokemon_a": pokemon_a,
        "pokemon_b": pokemon_b
    }
    r = requests.post(url, json=payload, headers=_headers(access_token), timeout=30)

    if r.status_code == 200:
        return True, r.json()

    try:
        return False, r.json()
    except:
        return False, {"detail": r.text}