from fastapi import FastAPI
from app.api.routers import auth, pokedex, collection, teams, ai

app = FastAPI()

app.include_router(auth.router, prefix="/auth")
app.include_router(pokedex.router)
app.include_router(collection.router)
app.include_router(teams.router)
app.include_router(ai.router)

@app.get("/")
def read_root():
    return {"message": "API running!"}

@app.get("/health")
def health():
    return {"status": "ok"}