from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from app.domain.repositories.collection_repository import CollectionRepository

def add_to_collection(db: Session, user_id: int, pokemon_id: int) -> dict:
    repo = CollectionRepository(db)
    if repo.exists(user_id, pokemon_id):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Already in collection")
    try:
        item = repo.add(user_id, pokemon_id)
        db.commit()               # <- importante
        return {"id": item.id, "pokemon_id": item.pokemon_id}
    except IntegrityError:
        db.rollback()
        # carrera / petición duplicada
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Already in collection")

def remove_from_collection(db: Session, user_id: int, pokemon_id: int) -> dict:
    repo = CollectionRepository(db)
    deleted = repo.remove(user_id, pokemon_id)
    db.commit()                   # <- importante
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not in collection")
    return {"removed": True, "pokemon_id": pokemon_id}

def list_collection_ids(db: Session, user_id: int) -> list[int]:
    repo = CollectionRepository(db)
    return repo.list_ids(user_id)