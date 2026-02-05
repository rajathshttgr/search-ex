from fastapi import FastAPI, Request, Response
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from models import Base
import uuid

from upload import upload_music

engine = create_engine(
    "sqlite:///./app.db",
    connect_args={"check_same_thread": False},
)

SessionLocal = sessionmaker(bind=engine)

app = FastAPI()
Base.metadata.create_all(bind=engine)


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


def get_db():
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
def read_root():
    return {"message": "search music!"}


@app.post("/audio/upload")
def upload_audio(request: Request):
    session_id = request.cookies.get("session_id")
    youtube_url = "https://youtu.be/Y8ZApXcnhy4?si=JgIrdz9qYe2oNKBe"
    success = upload_music(youtube_url, session_id)
    if success:
        return {"message": "audio uploaded successfully"}
    else:
        return {"message": "audio upload failed"}


@app.post("/audio/search")
def search_audio(request: Request):
    return {}


@app.get("/audio")
def list_all_audio(request: Request):
    return {}


@app.get("/audio/{music_id}")
def list_all_audio(request: Request):
    return {"id"}
