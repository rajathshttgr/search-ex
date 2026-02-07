import yt_dlp
from src.models import Music


def extract_metadata(url):
    ydl_opts = {
        "quiet": True,
        "skip_download": True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)

    return info


def preprocess_audio(youtube_url):
    # download audio
    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": "data/audio_file.%(ext)s",
        "quiet": True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([youtube_url])
    # normalize the audio
    # chunking of audio to 6-10 seconds clips
    # embedd list of chunk file paths
    # store those embeddings along with chunk id in vector db (qdrant)
    pass


def upload_music(youtube_url, session_id, db):

    # extra metadata and print
    metadata = extract_metadata(youtube_url)

    music = Music(
        session_id=session_id,
        youtube_url=youtube_url,
        title=metadata.get("title"),
        channel=metadata.get("uploader"),
        chunks_count=metadata.get("duration") // 6,
        chunk_length_s=6,
        sampling_rate=168,
        tags="music",
        status="processing",
    )
    db.add(music)
    db.commit()
    db.refresh(music)

    ## add following tasks to background worker
    preprocess_audio(youtube_url)

    return music.id


"""
HLD overview: upload songs to db, search by audio sample

- songs are preprocessed and chunked to 5-10 seconds clips and embedded using the external models.
So, now only embeddings are stored in vector db. embeddings ID is associated with meta data including
song url, time stamp, and some extra info like singer, song name, tags etc.
- query is 5-10 seconds audio clip which is processed and embedded using external model,
this embeddings is used to do search query, which returns top k similar chunk id along with the meta data.


DB Schema:

musics:
{
"music_id":"",
"youtube_url":"",
"song_name"?:"",
"music_composer"?:"",
"tags"?: ["pop", "indian"],
"chunks_count": 18,
"chunk_length":""
"sampling_rate":"",
}

chunks:
{
"chunk_id":"",
"music_id: "", (fk)
"temp_chunk_url":"",
}


Vector DB Schema:
{
"embedings" : which is generated from external model,
"chunk_id" : identifier
}
"""


"""
1. download music from youtube url and update musics metaadata in SQLite
2. normalize the audio
3. Chunking of audio and update chunks in SQLite
4. call embedding model by passing audio chunks
5. store those embeddings along with chunk id in vector db (qdrant)
6. return success
"""
