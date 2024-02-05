from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum
from typing import Dict
from app.database import Base, engine
from app.users.routers import router as users

# Creacion de la BD
Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users)

@app.get("/")
def root() -> Dict[str, object]:
    return {"message": "Bienvenido al backend EGZ"}

handler = Mangum(app)
