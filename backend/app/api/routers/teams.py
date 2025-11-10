from typing import List

from fastapi import APIRouter, Depends, Path
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.infra.db import get_db
from app.infra.orm import User
from app.domain.services import team_service
from app.domain.models.team import (
    TeamCreateDTO,
    TeamRenameDTO,
    TeamSummaryDTO,
    TeamDetailDTO,
)


router = APIRouter(prefix="/teams", tags=["Teams"])

@router.post(
    "",
    response_model=TeamDetailDTO,
    status_code=201,
    summary="Create a new Team",
    responses={
        201: {
            "description": "Team successfully created",
            "content": {
                "application/json": {
                    "example": {
                        "id": 5,
                        "name": "New Team",
                        "count": 0,
                        "members": []
                    }
                }
            }
        },
        401: {
            "description": "Unauthorized - Invalid or missing token",
            "content": {
                "application/json": {
                    "example": {"detail": "Invalid token"}
                }
            }
        },
        422: {
            "description": "Validation error - Missing or invalid fields",
            "content": {
                "application/json": {
                    "example": {
                        "detail": [
                            {
                                "type": "missing",
                                "loc": ["body", "name"],
                                "msg": "Field required",
                                "input": {}
                            }
                        ]
                    }
                }
            }
        },
    }
)
def create_team(
    data: TeamCreateDTO,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new Team associated with the authenticated user.

    The request must include a `name` field inside the JSON body.

    ### Request Body
    ```json
    {
        "name": "My Awesome Team"
    }
    ```

    ### Behavior
    - The team is created under the current authenticated user.
    - The name cannot be empty or blank.
    - The response returns the newly created Team with zero members.

    ### Returns
    A full `TeamDetailDTO` structure, including:
    - `id`: ID of the team
    - `name`: team name
    - `count`: number of members (initially 0)
    - `members`: empty list at creation time
    """
    return team_service.create_team(db, current_user.id, data.name)

@router.get(
    "",
    response_model=List[TeamSummaryDTO],
    summary="List all my Teams",
    description="Returns all Teams created by the authenticated user, including member count and creation date.",
    responses={
        200: {
            "description": "List of user's Teams successfully retrieved",
            "content": {
                "application/json": {
                    "example": [
                        {
                            "id": 4,
                            "name": "AI Squad",
                            "count": 6,
                            "created_at": "2025-11-11T06:59:15.959440"
                        },
                        {
                            "id": 2,
                            "name": "Pika",
                            "count": 3,
                            "created_at": "2025-11-11T02:17:26.104981"
                        },
                        {
                            "id": 1,
                            "name": "MightyTeam",
                            "count": 6,
                            "created_at": "2025-11-11T00:46:18.957789"
                        }
                    ]
                }
            }
        },
        401: {
            "description": "Unauthorized — missing or invalid access token",
            "content": {
                "application/json": {
                    "example": {"detail": "Invalid token"}
                }
            }
        }
    }
)
def list_my_teams(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retrieve all Teams created by the authenticated user.

    ## Description
    This endpoint returns the list of Teams belonging to the logged-in user.
    Each Team includes:
    - **id**: unique identifier  
    - **name**: name of the Team  
    - **count**: number of Pokémon currently in the Team  
    - **created_at**: timestamp of when the Team was created  

    ## Authentication
    Requires a valid Bearer token.  
    If missing or invalid → **401 Unauthorized**

    ## Response Example

    ```json
    [
        {
            "id": 4,
            "name": "AI Squad",
            "count": 6,
            "created_at": "2025-11-10T06:59:15.959440"
        },
        {
            "id": 2,
            "name": "Pika",
            "count": 3,
            "created_at": "2025-11-10T02:17:26.104981"
        },
        {
            "id": 1,
            "name": "MightyTeam",
            "count": 6,
            "created_at": "2025-11-10T00:46:18.957789"
        }
    ]
    ```

    ## Notes
    - Teams are sorted by creation date descending (newest first).
    - Useful for displaying all existing teams in the frontend.
    """
    return team_service.list_teams(db, current_user.id)


@router.get(
    "/{team_id}",
    response_model=TeamDetailDTO,
    summary="Get a specific Team with full details",
    responses={
        200: {
            "description": "Team successfully retrieved",
            "content": {
                "application/json": {
                    "example": {
                        "id": 1,
                        "name": "MightyTeam",
                        "count": 6,
                        "members": [
                            {
                                "id": 143,
                                "name": "snorlax",
                                "sprite": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/143.png",
                                "types": ["normal"]
                            },
                            {
                                "id": 144,
                                "name": "articuno",
                                "sprite": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/144.png",
                                "types": ["ice", "flying"]
                            },
                            {
                                "id": 145,
                                "name": "zapdos",
                                "sprite": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/145.png",
                                "types": ["electric", "flying"]
                            },
                            {
                                "id": 146,
                                "name": "moltres",
                                "sprite": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/146.png",
                                "types": ["fire", "flying"]
                            },
                            {
                                "id": 148,
                                "name": "dragonair",
                                "sprite": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/148.png",
                                "types": ["dragon"]
                            },
                            {
                                "id": 9,
                                "name": "blastoise",
                                "sprite": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/9.png",
                                "types": ["water"]
                            }
                        ]
                    }
                }
            }
        },
        401: {
            "description": "Unauthorized - Invalid or missing token",
            "content": {
                "application/json": {
                    "example": {"detail": "Invalid token"}
                }
            }
        },
        404: {
            "description": "Team not found or does not belong to the current user",
            "content": {
                "application/json": {
                    "example": {"detail": "Team not found"}
                }
            }
        }
    }
)
def get_team(
    team_id: int = Path(..., description="ID of the Team to retrieve"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retrieve a full detailed view of a specific Team, including all its members.

    ### Behavior
    - Only accessible to authenticated users.
    - Users can only view teams they own.
    - Returns:
      - team ID
      - team name
      - total member count
      - full list of Pokémon with basic info (id, name, sprite, types)

    ### Successful Response Example
    ```json
    {
        "id": 1,
        "name": "MightyTeam",
        "count": 6,
        "members": [
            { "id": 143, "name": "snorlax", "sprite": "...", "types": ["normal"] },
            { "id": 144, "name": "articuno", "sprite": "...", "types": ["ice","flying"] },
            ...
        ]
    }
    ```

    ### Errors
    - **401 Unauthorized:** Missing or invalid token.
    - **404 Not Found:** Team does not exist or belongs to another user.
    """
    return team_service.get_team(db, current_user.id, team_id)


@router.patch(
    "/{team_id}/rename",
    response_model=TeamDetailDTO,
    summary="Rename an existing Team",
    responses={
        200: {
            "description": "Team renamed successfully",
            "content": {
                "application/json": {
                    "example": {
                        "id": 1,
                        "name": "New Name",
                        "count": 6,
                        "members": [
                            {
                                "id": 143,
                                "name": "snorlax",
                                "sprite": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/143.png",
                                "types": ["normal"]
                            },
                            {
                                "id": 144,
                                "name": "articuno",
                                "sprite": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/144.png",
                                "types": ["ice", "flying"]
                            },
                            {
                                "id": 145,
                                "name": "zapdos",
                                "sprite": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/145.png",
                                "types": ["electric", "flying"]
                            },
                            {
                                "id": 146,
                                "name": "moltres",
                                "sprite": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/146.png",
                                "types": ["fire", "flying"]
                            },
                            {
                                "id": 148,
                                "name": "dragonair",
                                "sprite": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/148.png",
                                "types": ["dragon"]
                            },
                            {
                                "id": 9,
                                "name": "blastoise",
                                "sprite": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/9.png",
                                "types": ["water"]
                            }
                        ]
                    }
                }
            }
        },
        401: {
            "description": "Unauthorized - Invalid or missing token",
            "content": {
                "application/json": {
                    "example": {"detail": "Invalid token"}
                }
            }
        },
        404: {
            "description": "Team not found or not owned by the user",
            "content": {
                "application/json": {
                    "example": {"detail": "Team not found"}
                }
            }
        }
    }
)
def rename_team(
    team_id: int,
    data: TeamRenameDTO,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Rename an existing team owned by the current authenticated user.

    ### Behavior
    - Only authenticated users may rename teams.
    - Users may only rename teams they own.
    - A valid `new_name` is required.
    - Upon success, the endpoint returns the full updated `TeamDetailDTO`,
      including members and count.

    ### Request Body Example
    ```json
    {
        "name": "New Name"
    }
    ```

    ### Successful Response Example
    ```json
    {
        "id": 1,
        "name": "New Name",
        "count": 6,
        "members": [ ... ]
    }
    ```

    ### Errors
    - **401 Unauthorized:** Missing or invalid token.
    - **404 Not Found:** Team does not exist or does not belong to the user.
    """
    return team_service.rename_team(db, current_user.id, team_id, data.name)


@router.post(
    "/{team_id}/add/{pokemon_id}",
    response_model=TeamDetailDTO,
    summary="Add a Pokémon to an existing Team",
    responses={
        200: {
            "description": "Pokémon added successfully",
            "content": {
                "application/json": {
                    "example": {
                        "id": 5,
                        "name": "Hello",
                        "count": 1,
                        "members": [
                            {
                                "id": 149,
                                "name": "dragonite",
                                "sprite": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/149.png",
                                "types": ["dragon", "flying"]
                            }
                        ]
                    }
                }
            }
        },
        400: {
            "description": "Team is already full",
            "content": {
                "application/json": {
                    "example": {"detail": "Team full (max 6 pokemon)"}
                }
            }
        },
        401: {
            "description": "Unauthorized - missing or invalid token",
            "content": {
                "application/json": {
                    "example": {"detail": "Invalid token"}
                }
            }
        },
        404: {
            "description": "Team not found or not owned by user",
            "content": {
                "application/json": {
                    "example": {"detail": "Team not found"}
                }
            }
        }
    }
)
def add_member(
    team_id: int,
    pokemon_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Add a Pokémon to a specific team owned by the authenticated user.

    ### Behavior
    - Only the owner of the team can add Pokémon.
    - Teams can contain up to **6 Pokémon**.
    - Adding a Pokémon returns the full updated team structure.
    - Pokémon are validated to ensure they exist in the Pokédex.

    ### Parameters
    - **team_id**: ID of the team to modify.
    - **pokemon_id**: ID of the Pokémon to add.

    ### Successful Response Example
    ```json
    {
        "id": 5,
        "name": "Hello",
        "count": 1,
        "members": [
            {
                "id": 149,
                "name": "dragonite",
                "sprite": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/149.png",
                "types": ["dragon", "flying"]
            }
        ]
    }
    ```

    ### Errors
    - **400 Team full** — Teams cannot exceed 6 members.
    - **401 Unauthorized** — Token invalid or missing.
    - **404 Team not found** — The team doesn't exist or doesn't belong to the user.
    """
    return team_service.add_member(db, current_user.id, team_id, pokemon_id)


@router.delete(
    "/{team_id}/remove/{pokemon_id}",
    response_model=TeamDetailDTO,
    summary="Remove a Pokémon from a Team",
    responses={
        200: {
            "description": "Pokémon removed successfully (returns updated team)",
            "content": {
                "application/json": {
                    "example": {
                        "id": 5,
                        "name": "Hello",
                        "count": 0,
                        "members": []
                    }
                }
            }
        },
        401: {
            "description": "Unauthorized - missing or invalid token",
            "content": {
                "application/json": {
                    "example": {"detail": "Invalid token"}
                }
            }
        },
        404: {
            "description": "Team not found or Pokémon not in team",
            "content": {
                "application/json": {
                    "examples": {
                        "team_not_found": {
                            "summary": "Team does not exist",
                            "value": {"detail": "Team not found"}
                        },
                        "pokemon_not_in_team": {
                            "summary": "Pokémon not present in this team",
                            "value": {"detail": "Pokemon not in this team"}
                        }
                    }
                }
            }
        }
    }
)
def remove_member(
    team_id: int,
    pokemon_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Remove a Pokémon from one of the user's teams.

    ### Behavior
    - Only team owners can remove Pokémon.
    - Returns the updated team including all remaining members.
    - If the Pokémon is not present in the team, a 404 error is returned.
    - If the team does not exist or does not belong to the user, a 404 error is returned.

    ### Parameters
    - **team_id**: ID of the team to update.
    - **pokemon_id**: ID of the Pokémon to remove.

    ### Successful Response Example
    ```json
    {
        "id": 5,
        "name": "Hello",
        "count": 0,
        "members": []
    }
    ```

    ### Error Examples
    - Team not found:
        ```json
        {"detail": "Team not found"}
        ```
    - Pokémon not part of the team:
        ```json
        {"detail": "Pokemon not in this team"}
        ```
    - Unauthorized:
        ```json
        {"detail": "Invalid token"}
        ```
    """
    return team_service.remove_member(db, current_user.id, team_id, pokemon_id)


@router.delete(
    "/{team_id}",
    response_model=dict,
    summary="Delete a Team",
    responses={
        200: {
            "description": "Team deleted successfully",
            "content": {
                "application/json": {
                    "example": {"deleted": True}
                }
            }
        },
        401: {
            "description": "Unauthorized - missing or invalid token",
            "content": {
                "application/json": {
                    "example": {"detail": "Invalid token"}
                }
            }
        },
        404: {
            "description": "Team not found or does not belong to the user",
            "content": {
                "application/json": {
                    "example": {"detail": "Team not found"}
                }
            }
        }
    }
)
def delete_team(
    team_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete one of the user's Teams permanently.

    ### Behavior
    - The authenticated user must own the team.
    - Deletes the team and all its membership relationships.
    - Returns `{ "deleted": true }` on success.
    - Returns 404 if the team does not exist or does not belong to the user.

    ### Path Parameters
    - **team_id** — The ID of the team to delete.

    ### Successful Response Example
    ```json
    {
        "deleted": true
    }
    ```

    ### Error Responses
    - **401 Unauthorized**  
      ```json
      {"detail": "Invalid token"}
      ```

    - **404 Not Found**  
      ```json
      {"detail": "Team not found"}
      ```

    """
    return team_service.delete_team(db, current_user.id, team_id)