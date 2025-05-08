from fastapi import FastAPI
from .config import Config
from .routes import auth_router, knowledge_card_router, card_cluster_router
from fastapi.middleware.cors import CORSMiddleware

config = Config()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/api")
app.include_router(knowledge_card_router, prefix="/knowledge-card")
app.include_router(card_cluster_router, prefix="/suits")

@app.get("/")
def home():
    return {"message": "Brieffy Backend Running"}

__all__ = ["config", "app"]
