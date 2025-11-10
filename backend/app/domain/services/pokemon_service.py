import random
from typing import List, Dict, Any

from app.core.config import settings
from app.domain.models.pokemon import PokemonDTO
from app.infra.cache import local_cache
from app.infra import pokedapi

CACHE_TTL = settings.CACHE_TTL_SECONDS

def get_pokemon(name_or_id: str | int) -> PokemonDTO:
    key = f"pokemon:{str(name_or_id).lower()}"
    cached = local_cache.get(key)
    if cached:
        return PokemonDTO.model_validate(cached)

    raw = pokedapi.fetch_pokemon_raw(name_or_id)
    normalized = pokedapi.normalize_pokemon(raw)
    local_cache.set(key, normalized, CACHE_TTL)
    return PokemonDTO.model_validate(normalized)

def search_pokemon(query: str, limit: int = 20) -> List[Dict[str, Any]]:
    if not query or not query.strip():
        return []
    key = f"search:{query.lower()}:{limit}"
    cached = local_cache.get(key)
    if cached:
        return cached
    items = pokedapi.search_names(query, limit=limit)
    local_cache.set(key, items, CACHE_TTL)
    return items

def random_pokemon(max_id_hint: int = 1025, attempts: int = 5) -> PokemonDTO:
    """
    Selecciona un ID aleatorio dentro de un rango razonable (escala 1..1025 aprox).
    Reintenta algunos IDs si alguno no existe (por huecos).
    """
    for _ in range(attempts):
        pid = random.randint(1, max_id_hint)
        try:
            return get_pokemon(pid)
        except Exception:
            continue
    # fallback: pikachu
    return get_pokemon("pikachu")