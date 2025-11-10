from pydantic import BaseModel, Field
from typing import List

class PokemonStats(BaseModel):
    hp: int = 0
    attack: int = 0
    defense: int = 0
    special_attack: int = 0
    special_defense: int = 0
    speed: int = 0

class PokemonDTO(BaseModel):
    id: int
    name: str
    sprite: str | None = None
    types: List[str]
    stats: PokemonStats