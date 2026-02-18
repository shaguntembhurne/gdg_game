from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import os

from database import init_db, get_connection

app = FastAPI()

# Initialize DB on startup
init_db()

STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")


class ScoreSubmission(BaseModel):
    name: str
    score: int


@app.get("/leaderboard")
def get_leaderboard():
    conn = get_connection()
    rows = conn.execute(
        "SELECT name, score FROM scores ORDER BY score DESC LIMIT 3"
    ).fetchall()
    conn.close()
    return [{"name": row["name"], "score": row["score"]} for row in rows]


@app.post("/submit-score")
def submit_score(data: ScoreSubmission):
    if not data.name or not data.name.strip():
        raise HTTPException(status_code=400, detail="Name is required")
    conn = get_connection()
    conn.execute(
        "INSERT INTO scores (name, score) VALUES (?, ?)",
        (data.name.strip(), data.score),
    )
    conn.commit()
    conn.close()
    return {"status": "ok"}


GAME_ASSETS_DIR = os.path.join(STATIC_DIR, "game")

# duckhunt.js requests these assets relative to the page URL (/game),
# so the browser resolves them to the root level (e.g. /sprites.json).
@app.get("/sprites.json")
def serve_sprites_json():
    return FileResponse(os.path.join(GAME_ASSETS_DIR, "sprites.json"))

@app.get("/sprites.png")
def serve_sprites_png():
    return FileResponse(os.path.join(GAME_ASSETS_DIR, "sprites.png"))

@app.get("/audio.json")
def serve_audio_json():
    return FileResponse(os.path.join(GAME_ASSETS_DIR, "audio.json"))

@app.get("/audio.mp3")
def serve_audio_mp3():
    return FileResponse(os.path.join(GAME_ASSETS_DIR, "audio.mp3"))

@app.get("/audio.ogg")
def serve_audio_ogg():
    return FileResponse(os.path.join(GAME_ASSETS_DIR, "audio.ogg"))

@app.get("/game")
def serve_game():
    return FileResponse(os.path.join(STATIC_DIR, "game", "index.html"))


@app.get("/")
def serve_index():
    return FileResponse(os.path.join(STATIC_DIR, "index.html"))


# Mount static files AFTER explicit routes
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
