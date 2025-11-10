from pydantic import BaseModel

class CompareRequest(BaseModel):
    pokemon_a: str
    pokemon_b: str


class ComparedPokemon(BaseModel):
    id: int
    name: str
    sprite: str | None
    types: list[str]
    stats: dict


class CompareResponse(BaseModel):
    summary: str
    winner: str | None
    a: ComparedPokemon
    b: ComparedPokemon