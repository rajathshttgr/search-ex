from sqlalchemy import select
from fastapi import FastAPI, Request, Depends, BackgroundTasks
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel
from src.models import Base, Music
import uuid

from src.upload import upload_music, preprocess_audio

engine = create_engine(
    "sqlite:///./app.db",
    connect_args={"check_same_thread": False},
)

SessionLocal = sessionmaker(bind=engine)

app = FastAPI()
Base.metadata.create_all(bind=engine)


def get_db():
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()


sessions = {}


@app.middleware("http")
async def session_middleware(request: Request, call_next):
    session_id = request.cookies.get("session_id")

    if not session_id:
        session_id = str(uuid.uuid4())
        sessions[session_id] = {}
        response = await call_next(request)
        response.set_cookie("session_id", session_id)
        return response

    request.state.session = sessions.get(session_id, {})
    return await call_next(request)


@app.get("/")
def read_root():
    return {"message": "search music!"}


class UploadAudio(BaseModel):
    youtube_url: str


@app.post("/audio/upload")
def upload_audio(
    request: Request,
    upload_audio: UploadAudio,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    session_id = request.cookies.get("session_id")
    youtube_url = upload_audio.youtube_url
    music_id = upload_music(youtube_url, session_id, db)
    if music_id:
        background_tasks.add_task(preprocess_audio, youtube_url)
        return {
            "message": "audio upload task initialized successfully",
            "music_id": music_id,
        }
    else:
        return {"message": "failed to initialize audio upload task"}


class SearchAudio(BaseModel):
    query: str


@app.post("/audio/search")
def search_audio(request: Request, search_audio: SearchAudio):
    session_id = request.cookies.get("session_id")
    return {
        "message": f"search audio for query: {search_audio.query}",
        "session_id": session_id,
    }


@app.get("/audio")
def list_all_audio(
    request: Request, offset: int = 0, limit: int = 10, db: Session = Depends(get_db)
):
    session_id = request.cookies.get("session_id")

    stmt = (
        select(Music).where(Music.session_id == session_id).offset(offset).limit(limit)
    )
    music_list = db.execute(stmt).scalars().all()

    return music_list


@app.get("/audio/{music_id}")
def get_audio(request: Request, music_id: str, db: Session = Depends(get_db)):
    session_id = request.cookies.get("session_id")
    stmt = select(Music).where(Music.id == music_id and Music.session_id == session_id)
    music = db.execute(stmt).scalars().first()
    if not music:
        return {"message": "music not found"}
    return music
