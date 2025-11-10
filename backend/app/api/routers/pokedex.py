from fastapi import APIRouter, HTTPException, Query
from app.domain.services import pokemon_service
from app.domain.models.pokemon import PokemonDTO

router = APIRouter(prefix="/pokedex", tags=["Pokedex"])

@router.get(
    "/look/{id_or_name}",
    response_model=PokemonDTO,
    summary="Get Pokémon by name or ID",
    description="Returns detailed information about a Pokémon using its name or numerical ID.",
    responses={
        200: {
            "description": "Pokémon found successfully",
            "content": {
                "application/json": {
                    "example": {
                        "id": 25,
                        "name": "pikachu",
                        "sprite": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/25.png",
                        "types": ["electric"],
                        "stats": {
                            "hp": 35,
                            "attack": 55,
                            "defense": 40,
                            "special_attack": 50,
                            "special_defense": 50,
                            "speed": 90
                        }
                    }
                }
            }
        },
        404: {"description": "Pokémon not found"},
    },
)
def get_pokemon(id_or_name: str):
    """
    Fetch detailed information about a Pokémon.

    This endpoint retrieves Pokémon data from the internal Pokédex service,
    supporting both numeric IDs and textual names.

    ## Path Parameters
    - **id_or_name**: `str`  
      Pokémon identifier (e.g., `"25"`, `"pikachu"`, `"gengar"`).

    ## Returns
    A `PokemonDTO` object with the following fields:

    - **id**: `int`  
      Official Pokédex ID.
    - **name**: `str`  
      Lowercase Pokémon name.
    - **sprite**: `str`  
      URL to the official sprite image.
    - **types**: `list[str]`  
      One or two types (e.g., `["fire", "flying"]`).
    - **stats**: `dict` including:
        - `hp`
        - `attack`
        - `defense`
        - `special_attack`
        - `special_defense`
        - `speed`

    ## Error Handling
    - **404 Not Found**: Returned if the Pokémon does not exist.
    """
    try:
        return pokemon_service.get_pokemon(id_or_name)
    except Exception as e:
        raise HTTPException(status_code=404, detail="Pokémon not found") from e

@router.get(
    "/random",
    response_model=PokemonDTO,
    summary="Get a random Pokémon",
    description="Returns a random Pokémon from the internal Pokédex service.",
    responses={
        200: {
            "description": "Random Pokémon retrieved successfully",
            "content": {
                "application/json": {
                    "example": {
                        "id": 6,
                        "name": "charizard",
                        "sprite": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/6.png",
                        "types": ["fire", "flying"],
                        "stats": {
                            "hp": 78,
                            "attack": 84,
                            "defense": 78,
                            "special_attack": 109,
                            "special_defense": 85,
                            "speed": 100
                        }
                    }
                }
            }
        }
    },
)
def get_random():
    """
    Retrieve a random Pokémon from the Pokédex.

    This endpoint selects a Pokémon at random, returning the same data structure
    as the `/look/{id_or_name}` endpoint.

    ## Returns
    A `PokemonDTO` with:

    - **id**: `int` — Pokédex ID  
    - **name**: `str` — Pokémon name  
    - **sprite**: `str` — Image URL  
    - **types**: `list[str]` — One or two types  
    - **stats**: `dict` containing:
        - hp
        - attack
        - defense
        - special_attack
        - special_defense
        - speed

    ## Notes
    - The Pokémon is chosen randomly from the entire available dataset.
    """
    return pokemon_service.random_pokemon()

@router.get(
    "/search",
    summary="Search Pokémon by name",
    description="Returns a list of Pokémon whose names match a search query (case-insensitive, contains).",
    responses={
        200: {
            "description": "List of matching Pokémon",
            "content": {
                "application/json": {
                    "example": {
                        "items": [
                            {"id": 143, "name": "snorlax"},
                            {"id": 361, "name": "snorunt"},
                            {"id": 10206, "name": "snorlax-gmax"}
                        ]
                    }
                }
            }
        },
        422: {
            "description": "Validation error (usually missing or invalid query parameter)"
        }
    }
)
def search(
    query: str = Query(..., min_length=1, description="Search text (partial match, case-insensitive)."),
    limit: int = Query(
        20,
        ge=1,
        le=50,
        description="Maximum number of results to return (1–50)."
    )
):
    """
    Search Pokémon by partial or full name.

    This endpoint allows fuzzy searching: it returns Pokémon whose names
    **contain** the query text, not just exact matches.

    ## Query Parameters
    - **query** (`str`, required):  
      Substring to match against Pokémon names (case-insensitive).

    - **limit** (`int`, default=20):  
      Maximum number of results (between 1 and 50).

    ## Returns
    A JSON object containing:

    ```json
    {
      "items": [
        {"id": 143, "name": "snorlax"},
        {"id": 361, "name": "snorunt"},
        {"id": 10206, "name": "snorlax-gmax"}
      ]
    }
    ```

    - **id** may be an official Pokédex ID (1–1010+)  
      or a special form ID (e.g., Gigantamax, regional forms)

    - **name** is the normalized API identifier (lowercase with dashes)

    ## Notes
    - The search is **substring-based** and **case-insensitive**.
    - Useful for autocomplete, suggestions, and fast lookup.
    - Does not return full Pokémon details—only lightweight identifiers.
    """
    return {"items": pokemon_service.search_pokemon(query, limit=limit)}