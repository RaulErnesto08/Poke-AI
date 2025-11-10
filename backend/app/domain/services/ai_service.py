import base64
from fastapi import HTTPException
from openai import OpenAI

from app.core.config import settings
from app.domain.models.ai import VisionIdentifyResult


def identify_pokemon_with_vision(image_bytes: bytes) -> VisionIdentifyResult:
    if not settings.OPENAI_API_KEY:
        raise HTTPException(500, "OPENAI_API_KEY not configured")

    client = OpenAI(api_key=settings.OPENAI_API_KEY)

    # convert to base64 string
    b64 = base64.b64encode(image_bytes).decode("utf-8")

    input_data = [
        {
            "role": "system",
            "content": (
                "You are a Pokémon identifier. Return the name of the Pokémon "
                "in English, a confidence score, and a short rationale. "
                "If unsure, return up to 3 candidates ordered by confidence."
            ),
        },
        {
            "role": "user",
            "content": [
                {"type": "input_text", "text": "Identify the Pokémon."},
                {
                    "type": "input_image",
                    "image_url": f"data:image/jpeg;base64,{b64}",
                },
            ],
        },
    ]

    try:
        response = client.responses.parse(
            model=settings.OPENAI_MODEL or "gpt-4o-mini",
            input=input_data,
            text_format=VisionIdentifyResult,
        )

        return response.output_parsed

    except Exception as e:
        raise HTTPException(500, f"AI error: {e}")