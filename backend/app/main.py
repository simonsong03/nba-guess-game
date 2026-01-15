from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import game

app = FastAPI(
    title="NBA Wordle API",
    description="Backend API for NBA Wordle game",
    version="1.0.0"
)

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(game.router, prefix="/api", tags=["game"])

@app.get("/")
def root():
    return {"message": "NBA Wordle API", "status": "running"}

@app.get("/health")
def health():
    return {"status": "healthy"}
