from fastapi import APIRouter, Depends, Path
from sqlalchemy.orm import Session
from app.core.dependencies import get_current_user
from app.infra.db import get_db
from app.domain.services import collection_service
from app.infra.orm import User

router = APIRouter(prefix="/collection", tags=["Collection"])

@router.get(
    "",
    summary="List my Pokémon collection",
    description="Returns the list of Pokémon IDs stored in the authenticated user's personal collection.",
    responses={
        200: {
            "description": "Collection retrieved successfully",
            "content": {
                "application/json": {
                    "example": {
                        "items": [150, 149, 445, 6, 3, 25, 9, 143]
                    }
                }
            }
        },
        401: {
            "description": "Unauthorized — invalid or missing token",
            "content": {
                "application/json": {
                    "example": {"detail": "Invalid token"}
                }
            }
        }
    }
)
def list_collection(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Retrieve the authenticated user's Pokémon collection.

    ## Description
    This endpoint returns a list of Pokémon IDs representing all Pokémon
    saved to the user's personal collection.

    The IDs correspond to their Pokédex identifiers, and can be used
    elsewhere in the API to fetch full Pokémon details.

    ## Authentication
    - Requires a valid **Bearer access token**
    - If the token is missing or invalid → returns **401 Unauthorized**

    ## Returns
    A JSON object with:

    ```json
    {
      "items": [150, 149, 445, 6, 3, 25, 9, 143]
    }
    ```

    - The array **may be empty** if the user has not saved any Pokémon.
    - The items are ordered by most recently added (descending).

    ## Error Responses
    - **401 Unauthorized**  
      Returned when the request does not include a valid access token.

    ## Notes
    - This endpoint returns only IDs, not full Pokémon data.
    - Use `/pokedex/look/{id_or_name}` to fetch full Pokémon information.
    """
    ids = collection_service.list_collection_ids(db, current_user.id)
    return {"items": ids}

@router.post(
    "/add/{pokemon_id}",
    summary="Add a Pokémon to my collection",
    description="Adds the specified Pokémon to the authenticated user's personal collection.",
    responses={
        200: {
            "description": "Pokémon successfully added to the collection",
            "content": {
                "application/json": {
                    "example": {"id": 23, "pokemon_id": 14}
                }
            },
        },
        409: {
            "description": "Pokémon already exists in the user's collection",
            "content": {
                "application/json": {
                    "example": {"detail": "Already in collection"}
                }
            },
        },
        401: {
            "description": "Unauthorized — missing or invalid access token",
            "content": {
                "application/json": {
                    "example": {"detail": "Invalid token"}
                }
            },
        },
    },
)
def add_collection(
    pokemon_id: int = Path(..., ge=1, description="Pokédex ID of the Pokémon to add"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Add a Pokémon to the authenticated user's collection.

    ## Description
    This endpoint adds a Pokémon identified by its numeric Pokédex ID to the
    current user's personal collection.

    If the Pokémon is already present, the API responds with **409 Conflict**.

    ## Authentication
    Requires a valid Bearer token.  
    If missing or invalid → **401 Unauthorized**

    ## Parameters
    - **pokemon_id** (path, integer):  
      The Pokédex ID of the Pokémon to store in the user's collection.

    ## Returns
    A JSON object containing:

    ```json
    {
      "id": 23,
      "pokemon_id": 14
    }
    ```

    - `id`: internal database identifier of the collection entry  
    - `pokemon_id`: the Pokédex identifier of the stored Pokémon

    ## Error Responses
    ### 409 — Pokémon already in collection
    Returned when trying to store a duplicate Pokémon.

    ### 401 — Unauthorized  
    Returned when the access token is invalid or missing.

    ## Notes
    - Pokémon IDs must be numeric and ≥ 1.
    - Real Pokémon may have IDs up to 1025+ depending on your dataset.
    """
    return collection_service.add_to_collection(db, current_user.id, pokemon_id)

@router.delete(
    "/remove/{pokemon_id}",
    summary="Remove a Pokémon from my collection",
    description="Removes the specified Pokémon from the authenticated user's personal collection, if present.",
    responses={
        200: {
            "description": "Pokémon successfully removed from the collection",
            "content": {
                "application/json": {
                    "example": {"removed": True, "pokemon_id": 14}
                }
            },
        },
        404: {
            "description": "The Pokémon is not found in the user's collection",
            "content": {
                "application/json": {
                    "example": {"detail": "Not in collection"}
                }
            },
        },
        401: {
            "description": "Unauthorized — missing or invalid access token",
            "content": {
                "application/json": {
                    "example": {"detail": "Invalid token"}
                }
            },
        },
    },
)
def remove_collection(
    pokemon_id: int = Path(..., ge=1, description="Pokédex ID of the Pokémon to remove"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Remove a Pokémon from the authenticated user's collection.

    ## Description
    This endpoint deletes a Pokémon—identified by its Pokédex ID—from the user's
    collection.  
    If the Pokémon is not currently stored, the API returns **404 Not Found**.

    ## Authentication
    Requires a valid Bearer token.  
    If missing or invalid → **401 Unauthorized**

    ## Parameters
    - **pokemon_id** (path, integer):  
      The Pokédex ID of the Pokémon to remove.

    ## Returns
    A JSON response confirming the deletion:

    ```json
    {
      "removed": true,
      "pokemon_id": 14
    }
    ```

    - `removed`: indicates the removal operation was successful  
    - `pokemon_id`: the ID of the Pokémon that was removed

    ## Error Responses

    ### 404 — Not in collection
    Returned when the user tries to remove a Pokémon that is not present in the collection.

    ### 401 — Unauthorized  
    Returned when the access token is missing or invalid.

    ## Notes
    - Pokémon IDs must be numeric and ≥ 1.
    - The operation is idempotent. If already removed, it returns an error **404**.
    """
    return collection_service.remove_from_collection(db, current_user.id, pokemon_id)