import re
import httpx
from tenacity import retry, stop_after_attempt, wait_fixed
from typing import Any, Dict, List, Optional

from app.core.config import settings

def _pokemon_url(name_or_id: str | int) -> str:
    return f"{settings.POKEAPI_BASE_URL}/pokemon/{name_or_id}"

def _pokemon_list_url(limit: int = 2000, offset: int = 0) -> str:
    return f"{settings.POKEAPI_BASE_URL}/pokemon?limit={limit}&offset={offset}"

@retry(stop=stop_after_attempt(settings.POKEAPI_RETRIES), wait=wait_fixed(0.4))
def _get(url: str) -> Dict[str, Any]:
    with httpx.Client(timeout=settings.POKEAPI_TIMEOUT_SECONDS) as client:
        r = client.get(url)
        r.raise_for_status()
        return r.json()

def fetch_pokemon_raw(name_or_id: str | int) -> Dict[str, Any]:
    """Obtiene el JSON crudo de /pokemon/{id|name} (lanza httpx.HTTPStatusError si 404)."""
    return _get(_pokemon_url(name_or_id))

def search_names(query: str, limit: int = 20) -> List[Dict[str, Any]]:
    """
    Descarga listado grande de nombres/urls y filtra por contains.
    Retorna [{'id': int, 'name': str}] (top N).
    """
    data = _get(_pokemon_list_url(limit=2000, offset=0))
    results = data.get("results", [])
    q = query.strip().lower()
    out = []
    for item in results:
        name = item["name"]
        if q in name:
            # id viene en la url: .../pokemon/{id}/
            m = re.search(r"/pokemon/(\d+)/?$", item["url"])
            pid = int(m.group(1)) if m else None
            out.append({"id": pid, "name": name})
            if len(out) >= limit:
                break
    return out

def normalize_pokemon(raw: Dict[str, Any]) -> Dict[str, Any]:
    """Convierte el JSON de PokeAPI a nuestro DTO dict."""
    stats_map = {
        "hp": 0,
        "attack": 0,
        "defense": 0,
        "special-attack": 0,
        "special-defense": 0,
        "speed": 0,
    }
    for s in raw.get("stats", []):
        name = s["stat"]["name"]
        base = s["base_stat"]
        if name in stats_map:
            stats_map[name] = base

    types = [t["type"]["name"] for t in sorted(raw.get("types", []), key=lambda x: x.get("slot", 0))]
    sprite = (raw.get("sprites") or {}).get("front_default")

    return {
        "id": raw["id"],
        "name": raw["name"],
        "sprite": sprite,
        "types": types,
        "stats": {
            "hp": stats_map["hp"],
            "attack": stats_map["attack"],
            "defense": stats_map["defense"],
            "special_attack": stats_map["special-attack"],
            "special_defense": stats_map["special-defense"],
            "speed": stats_map["speed"],
        },
    }