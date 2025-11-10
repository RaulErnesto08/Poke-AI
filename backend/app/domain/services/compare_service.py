from openai import OpenAI
from fastapi import HTTPException
from app.core.config import settings
from app.domain.models.compare import CompareRequest, CompareResponse, ComparedPokemon
from app.domain.services.pokemon_service import get_pokemon


client = OpenAI(api_key=settings.OPENAI_API_KEY)

SYSTEM_PROMPT = """
You are a Pokémon analyst. You compare two Pokémon and explain:
- strengths
- weaknesses
- stat differences
- type matchups
- strategic advantage
- which one would likely win a fair battle

Return the winner's NAME only (not ID), or "tie" if no clear winner.
The main response should be a detailed summary.
"""


def compare_pokemon(req: CompareRequest) -> CompareResponse:
    # Fetch Pokémon data
    try:
        poke_a = get_pokemon(req.pokemon_a)
        poke_b = get_pokemon(req.pokemon_b)
    except Exception:
        raise HTTPException(404, "One of the Pokémon could not be found")

    # Build structured input text
    content = f"""
Compare Pokémon A and B.

### Pokémon A
Name: {poke_a.name}
Types: {poke_a.types}
Stats: {poke_a.stats}

### Pokémon B
Name: {poke_b.name}
Types: {poke_b.types}
Stats: {poke_b.stats}

Provide:
- A detailed comparison summary
- The predicted winner by NAME only (or "tie")
"""

    response = client.responses.create(
        model="gpt-4.1",
        input=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            },
            {
                "role": "user",
                "content": content
            },
        ]
    )

    output = response.output_text.strip()

    # Split into summary + winner
    # Expect format: "summary...\nWINNER: Pikachu"
    lines = output.split("\n")
    winner = None
    summary = output

    for line in lines:
        if line.lower().startswith("winner"):
            winner = line.split(":")[-1].strip()
            break

    if winner is None:
        # fallback
        winner = poke_a.name

    return CompareResponse(
        summary=summary,
        winner=winner,
        a=ComparedPokemon(
            id=poke_a.id,
            name=poke_a.name,
            sprite=poke_a.sprite,
            types=poke_a.types,
            stats=poke_a.stats.model_dump(),
        ),
        b=ComparedPokemon(
            id=poke_b.id,
            name=poke_b.name,
            sprite=poke_b.sprite,
            types=poke_b.types,
            stats=poke_b.stats.model_dump(),
        ),
    )