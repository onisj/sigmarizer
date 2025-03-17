from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from summarizer import summarize_youtube_video
import os

app = FastAPI()

# Mount static files (CSS and JS)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Set up Jinja2 templates
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "summary": None, "video_url": None, "sentiment": None, "tts_enabled": False}
    )

@app.post("/", response_class=HTMLResponse)
async def summarize(request: Request, query: str = Form(...), summary_style: str = Form(...), tts_enabled: bool = Form(False)):
    # For form submission (fallback if JS is disabled)
    result = summarize_youtube_video(query, summary_style=summary_style, tts_enabled=tts_enabled)
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "summary": result["summary"],
            "video_url": result["video_url"],
            "sentiment": result["sentiment"],
            "tts_enabled": tts_enabled
        }
    )

@app.post("/api/summarize", response_class=JSONResponse)
async def api_summarize(query: str = Form(...), summary_style: str = Form(...), tts_enabled: bool = Form(False)):
    # API endpoint returning JSON
    try:
        result = summarize_youtube_video(query, summary_style=summary_style, tts_enabled=tts_enabled)
        return result
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.get("/play_audio")
async def play_audio():
    audio_file = "summary.mp3"
    if os.path.exists(audio_file):
        return FileResponse(audio_file, media_type="audio/mpeg")
    return {"error": "Audio not available"}, 404

# Run with: uvicorn main:app --reload