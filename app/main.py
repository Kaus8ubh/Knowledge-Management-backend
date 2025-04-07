from fastapi import FastAPI
from routes import auth_router, knowledge_card_router, card_cluster_router

app = FastAPI()
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(auth_router, prefix="/api")
app.include_router(knowledge_card_router,prefix="/knowledge-card")
app.include_router(card_cluster_router, prefix="/suits")

@app.get("/")
def home():
    return {"message": "Brieffy Backend Running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=5000, reload=True)