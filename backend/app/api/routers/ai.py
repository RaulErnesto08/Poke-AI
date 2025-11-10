from fastapi import APIRouter, File, UploadFile, Depends
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.infra.db import get_db
from app.infra.orm import User
from app.domain.services.ai_service import identify_pokemon_with_vision
from app.domain.services.pokemon_service import search_pokemon, get_pokemon
from app.domain.models.ai import VisionIdentifyResult
from app.domain.models.compare import CompareRequest, CompareResponse
from app.domain.services.compare_service import compare_pokemon
from app.domain.services.recommend_service import recommend_for_user
from app.domain.services.auto_team_service import build_auto_team
from app.domain.services.fun_facts_service import get_fun_facts

router = APIRouter(prefix="/ai", tags=["AI"])


@router.post(
    "/identify",
    summary="Identify a Pokémon from an uploaded image",
    responses={
        200: {
            "description": "Pokémon identified successfully",
            "content": {
                "application/json": {
                    "examples": {
                        "pikachu": {
                            "summary": "Identifies Pikachu",
                            "value": {
                                "ai": {
                                    "primary_name": "Pikachu",
                                    "candidates": [],
                                    "rationale": "The Pokémon in the image has distinctive yellow fur, long ears with black tips..."
                                },
                                "match": {
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
                        },
                        "snorlax_with_candidates": {
                            "summary": "Identifies Snorlax with candidate list",
                            "value": {
                                "ai": {
                                    "primary_name": "Snorlax",
                                    "candidates": [
                                        {"name": "Snorlax", "confidence": 0.95},
                                        {"name": "Munchlax", "confidence": 0.04},
                                        {"name": "Wobbuffet", "confidence": 0.01}
                                    ],
                                    "rationale": "The Pokémon depicted is a large, round creature with a sleepy face..."
                                },
                                "match": {
                                    "id": 143,
                                    "name": "snorlax",
                                    "sprite": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/143.png",
                                    "types": ["normal"],
                                    "stats": {
                                        "hp": 160,
                                        "attack": 110,
                                        "defense": 65,
                                        "special_attack": 65,
                                        "special_defense": 110,
                                        "speed": 30
                                    }
                                }
                            }
                        }
                    }
                }
            }
        },
        401: {
            "description": "Unauthorized — missing or invalid token",
            "content": {
                "application/json": {
                    "example": {"detail": "Invalid token"}
                }
            }
        }
    }
)
def ai_identify(
    image: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Identify a Pokémon using AI Vision capabilities.

    ### Description
    This endpoint analyzes an uploaded image using an AI Vision model and returns:
    - The AI's best guess (`primary_name`)
    - Alternative candidate names with confidence scores (if available)
    - An explanation (`rationale`)
    - A resolved match using the internal Pokédex API

    The system attempts to match the AI-identified Pokémon with real Pokédex data:
    - First using the primary name
    - Then trying the candidate list (if provided)

    ### Request
    - **image**: A PNG/JPEG image containing a Pokémon.

    ### Successful Responses

    #### Pikachu Example
    ```json
    {
      "ai": {
        "primary_name": "Pikachu",
        "candidates": [],
        "rationale": "The Pokémon in the image has distinctive yellow fur..."
      },
      "match": {
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
    ```

    #### Snorlax (with candidates) Example
    ```json
    {
      "ai": {
        "primary_name": "Snorlax",
        "candidates": [
          {"name": "Snorlax", "confidence": 0.95},
          {"name": "Munchlax", "confidence": 0.04},
          {"name": "Wobbuffet", "confidence": 0.01}
        ],
        "rationale": "The Pokémon depicted is a large, round creature..."
      },
      "match": {
        "id": 143,
        "name": "snorlax",
        "sprite": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/143.png",
        "types": ["normal"],
        "stats": {
          "hp": 160,
          "attack": 110,
          "defense": 65,
          "special_attack": 65,
          "special_defense": 110,
          "speed": 30
        }
      }
    }
    ```

    ### Errors
    - **401 Unauthorized**
        - Missing or invalid access token
    """

    image_bytes = image.file.read()

    ai_result: VisionIdentifyResult = identify_pokemon_with_vision(image_bytes)

    # Resolver el primary_name con nuestra API
    match = None
    candidates = ai_result.candidates

    # Primero intentamos primary_name
    items = search_pokemon(ai_result.primary_name, limit=1)
    if items:
        key = items[0].get("name") or items[0].get("id")
        if key:
            try:
                match = get_pokemon(key)
            except Exception:
                match = None

    # Si no match → intentar candidatos
    if match is None:
        for c in candidates:
            items = search_pokemon(c.name, limit=1)
            if items:
                key = items[0].get("name") or items[0].get("id")
                try:
                    match = get_pokemon(key)
                    break
                except Exception:
                    continue

    return {
        "ai": ai_result,
        "match": match,
    }
    
@router.post(
    "/compare",
    response_model=CompareResponse,
    summary="Compare two Pokémon using AI analysis",
    responses={
        200: {
            "description": "AI-generated Pokémon comparison",
            "content": {
                "application/json": {
                    "example": {
                        "summary": "### Detailed Comparison Summary\n\n#### **Strengths**\n**Charizard**\n- Excellent Special Attack (109) and Speed (100)...",
                        "winner": "charizard",
                        "a": {
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
                        },
                        "b": {
                            "id": 9,
                            "name": "blastoise",
                            "sprite": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/9.png",
                            "types": ["water"],
                            "stats": {
                                "hp": 79,
                                "attack": 83,
                                "defense": 100,
                                "special_attack": 85,
                                "special_defense": 105,
                                "speed": 78
                            }
                        }
                    }
                }
            }
        },
        400: {
            "description": "Invalid Pokémon name or ID",
            "content": {
                "application/json": {
                    "example": {"detail": "Pokemon 'xyz' not found"}
                }
            }
        },
        422: {
            "description": "Validation error (missing fields or invalid body format)",
            "content": {
                "application/json": {
                    "example": {
                        "detail": [
                            {
                                "loc": ["body", "pokemon_a"],
                                "msg": "Field required",
                                "type": "value_error.missing"
                            }
                        ]
                    }
                }
            }
        }
    }
)
def compare(req: CompareRequest):
    """
    Compare two Pokémon using an AI-powered statistical and strategic evaluation.

    ### Description
    This endpoint generates a detailed comparison between two Pokémon using:
    - Stats (HP, Attack, Defense, Sp. Attack, Sp. Defense, Speed)
    - Type advantages and weaknesses
    - Strategic roles (sweeper, tank, support)
    - Matchup predictions

    The AI returns:
    - A Markdown-formatted analysis summary
    - Detailed Pokémon objects (`a` and `b`)
    - A predicted winner

    ### Request Body
    Example:
    ```json
    {
        "pokemon_a": "charizard",
        "pokemon_b": "blastoise"
    }
    ```

    Pokémon can be provided as:
    - name: `"pikachu"`, `"snorlax"`, `"charizard"`
    - ID: `25`, `143`, `6`

    ### Successful Response Example
    ```json
    {
        "summary": "### Detailed Comparison Summary...",
        "winner": "charizard",
        "a": {...},
        "b": {...}
    }
    ```

    ### Error Cases
    #### 400 — Pokémon not found
    Occurs if either `pokemon_a` or `pokemon_b` is invalid.

    ```json
    { "detail": "Pokemon 'xyz' not found" }
    ```

    #### 422 — Bad request
    Missing or malformed fields.

    ```json
    {
        "detail": [{
            "loc": ["body", "pokemon_a"],
            "msg": "Field required",
            "type": "value_error.missing"
        }]
    }
    ```

    #### 401 — Unauthorized
    Missing or invalid token.

    ### Notes
    - Analysis is generated dynamically using AI.
    - Summary is Markdown-ready.
    - Winner may differ from summary emphasis (AI reasoning).
    """
    return compare_pokemon(req)

@router.post(
    "/recommendations",
    summary="Get personalized Pokémon recommendations using AI",
    responses={
        200: {
            "description": "AI-generated recommendations based on the user's collection",
            "content": {
                "application/json": {
                    "example": {
                        "summary": "Your team contains a broad mix of types, including strong representation of Steel, Flying, Ghost...",
                        "recommendations": [
                            {
                                "id": None,
                                "name": "Tapu Fini",
                                "sprite": None,
                                "types": [],
                                "reason": "Water/Fairy typing gives a strong answer..."
                            },
                            {
                                "id": 10008,
                                "name": "rotom-heat",
                                "sprite": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/10008.png",
                                "types": ["electric", "fire"],
                                "reason": "Electric/Fire typing offers immunity..."
                            }
                        ]
                    }
                }
            }
        },
        401: {
            "description": "Unauthorized",
            "content": {
                "application/json": {
                    "example": {"detail": "Invalid token"}
                }
            }
        }
    }
)
def ai_recommendations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Generate personalized Pokémon recommendations for the authenticated user.

    ### Description
    This endpoint analyzes the user's current collection and suggests Pokémon
    that improve:
    - type coverage
    - team balance
    - defensive synergy
    - offensive versatility
    - redundancy reduction

    The AI considers:
    - type weaknesses and resistances
    - role distribution (tank, sweeper, support, pivot)
    - stat spreads
    - dual-type synergy
    - hazards and support options

    Returned recommendations may include Pokémon outside the user’s current roster.
    Some recommendations may lack valid IDs or sprites (e.g., special forms or non-standard entries).

    ### Response Format
    ```json
    {
      "summary": "Detailed analysis of your overall team composition...",
      "recommendations": [
        {
          "id": 823,
          "name": "corviknight",
          "sprite": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/823.png",
          "types": ["flying", "steel"],
          "reason": "Steel/Flying type improves bulk and hazard control..."
        }
      ]
    }
    ```

    ### Error Responses
    #### 401 Unauthorized
    Returned when no valid token is provided:
    ```json
    { "detail": "Invalid token" }
    ```

    ### Notes
    - Recommendations are AI-generated and may include non-canonical variants.
    - Invalid or missing Pokémon (id=null) should be filtered in the frontend.
    - The analysis summary is designed for natural-language display.
    """
    return recommend_for_user(db, current_user.id)

@router.post(
    "/auto-team",
    summary="Generate an optimal Pokémon team using AI",
    responses={
        200: {
            "description": "AI-generated balanced team based on the user's collection",
            "content": {
                "application/json": {
                    "example": {
                        "summary": "This team covers a variety of types and ensures both offensive and defensive capabilities.",
                        "team": [
                            {
                                "id": 445,
                                "name": "garchomp",
                                "sprite": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/445.png",
                                "types": ["dragon", "ground"],
                                "stats": {
                                    "hp": 108,
                                    "attack": 130,
                                    "defense": 95,
                                    "special_attack": 80,
                                    "special_defense": 85,
                                    "speed": 102
                                },
                                "reason": "Garchomp is a versatile Dragon/Ground type with powerful offensive and defensive stats."
                            }
                        ]
                    }
                }
            }
        },
        401: {
            "description": "Unauthorized",
            "content": {
                "application/json": {
                    "example": {"detail": "Invalid token"}
                }
            }
        }
    }
)
def ai_auto_team(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Generate a fully-optimized Pokémon team using AI.

    ### Description
    This endpoint analyzes the user's entire collection and automatically selects
    the best possible combination of **six Pokémon** to form a balanced and powerful team.

    The AI ensures:
    - ✅ Type coverage  
    - ✅ Offensive/defensive balance  
    - ✅ Synergy between teammates  
    - ✅ Reduced redundancy (avoid too many of the same type)  
    - ✅ Strong overall stats and role distribution  
    - ✅ Compatibility for typical battle scenarios  

    Returned results include:
    - Pokémon ID  
    - Official sprite URL  
    - Types  
    - Stats (hp, attack, defense, special stats, speed)  
    - AI reasoning explaining why each Pokémon was chosen  

    ### Response Format
    ```json
    {
      "summary": "High-level explanation of the team strategy",
      "team": [
        {
          "id": 445,
          "name": "garchomp",
          "sprite": "https://.../445.png",
          "types": ["dragon", "ground"],
          "stats": {...},
          "reason": "Why the AI picked this Pokémon"
        }
      ]
    }
    ```

    ### Notes
    - The validation ensures the user has a valid session (401 otherwise).
    - All selected Pokémon MUST exist in the PokeAPI (invalid items are filtered automatically).
    - If the user has fewer than 6 Pokémon in their collection, the AI still builds the best team possible.

    ### Errors
    #### 401 Unauthorized
    Returned when the request does not include a valid bearer token:
    ```json
    { "detail": "Invalid token" }
    ```

    """
    return build_auto_team(db, current_user.id)


@router.get(
    "/fun-facts/{pokemon_name}",
    summary="Get AI-generated fun facts about a Pokémon",
    responses={
        200: {
            "description": "Fun facts and a summary generated by AI",
            "content": {
                "application/json": {
                    "example": {
                        "pokemon": "Snorlax",
                        "summary": "Snorlax is a giant, sleepy creature known for its voracious appetite and gentle nature...",
                        "fun_facts": [
                            {
                                "fact": "Snorlax eats over 800 pounds of food a day.",
                                "relevance": "This highlights its insatiable appetite and signature behavior."
                            },
                            {
                                "fact": "It can sleep anywhere, spreading out its massive body without a care.",
                                "relevance": "Explains why Snorlax often blocks paths in games."
                            }
                        ]
                    }
                }
            }
        },
        404: {
            "description": "Pokémon not found",
            "content": {
                "application/json": {
                    "example": {"detail": "Pokémon not found"}
                }
            }
        }
    }
)
def fun_facts(pokemon_name: str):
    """
    Generate fun facts and a short AI-crafted summary for a Pokémon.

    ### Description
    This endpoint provides an AI-generated set of fun facts about a specific Pokémon,
    including a short descriptive summary and multiple interesting trivia items.

    The AI output includes:
    - ✅ A brief personality/style description  
    - ✅ 4–8 fun facts  
    - ✅ An explanation of why each fact is relevant  

    Returned structure:
    ```json
    {
      "pokemon": "Snorlax",
      "summary": "...",
      "fun_facts": [
        {"fact": "Text...", "relevance": "Why this is interesting"},
        ...
      ]
    }
    ```

    ### Behavior
    - If the Pokémon exists according to the PokeAPI name or ID → returns AI-generated info.
    - If the name is unrecognized → raises **404 Pokémon not found**.
    - Name matching is case-insensitive and supports hyphens (e.g., “mr-mime”, “ho-oh”).

    ### Notes
    - The AI may generate lore or trivia inspired by the Pokémon universe.
    - Facts are not guaranteed to be official canon but are generated creatively.
    - This endpoint does not require user authentication.

    """
    return get_fun_facts(pokemon_name)