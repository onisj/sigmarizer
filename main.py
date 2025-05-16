from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from summarizer import summarize_youtube_video

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def get_form():
    with open("templates/index.html") as f:
        return HTMLResponse(content=f.read())

@app.post("/api/summarize")
async def summarize(query: str = Form(...), summary_style: str = Form(...), tts_enabled: bool = Form(False)):
    result = summarize_youtube_video(query, summary_style, tts_enabled)
    return result

@app.get("/play_audio")
async def play_audio():
    return FileResponse("summary.mp3")