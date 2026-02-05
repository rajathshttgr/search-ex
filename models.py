from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Music(Base):
    __tablename__ = "music"
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String)
    youtube_url = Column(String)
    title = Column(String)
    channel = Column(String)
    chunks_count = Column(Integer)
    chunk_length_s = Column(Integer)
    sampling_rate = Column(Integer)
    tags = Column(String)
    status = Column(String)


class AudioChunk(Base):
    __tablename__ = "audio_chunk"
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String)
    music_id = Column(Integer)
    status = Column(String)
    temp_chunk_url = Column(String)
