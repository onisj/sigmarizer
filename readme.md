# SIgmarizer: YouTube Video Summarizer

This is a FastAPI-based web application that summarizes YouTube videos by extracting their transcripts, generating detailed summaries in various styles, performing sentiment analysis, and optionally converting summaries to speech. The application leverages AI models and APIs to provide comprehensive and engaging outputs.

## Features

- Search for YouTube videos by query and retrieve the top result.
- Extract transcripts from YouTube videos using the `youtube_transcript_api`.
- Generate detailed summaries (500+ words) in specified styles (e.g., concise, detailed, casual) using Grok's `llama-3.3-70b-versatile` model via the `groq` API.
- Perform sentiment analysis (250+ words) on the transcript, identifying overall sentiment, specific emotions, and key phrases.
- Optionally convert summaries to audio using Google Text-to-Speech (`gTTS`).
- Serve a simple web interface for user interaction and provide API endpoints for programmatic access.

## How It Works

1. **Web Interface**: Users access the app via a browser at `GET /`, which serves an HTML form (`index.html`) for inputting a YouTube query, summary style, and text-to-speech option.
2. **API Request**: The form submits a `POST /api/summarize` request with the query, style, and TTS preference.
3. **Video Search**: The app searches YouTube using the `google-api-python-client` to find the video URL and thumbnail.
4. **Transcript Extraction**: The transcript is fetched using `youtube_transcript_api` with proxy support for reliability.
5. **Processing**: The transcript is processed with Grok's AI model to generate a summary and sentiment analysis using predefined tools.
6. **Audio (Optional)**: If TTS is enabled, the summary is converted to an MP3 file and played.
7. **Response**: The API returns a JSON object with the summary, video URL, sentiment analysis, and thumbnail URL.
8. **Audio Playback**: Users can access the generated audio via `GET /play_audio`.

## Prerequisites

- Python 3.8+
- API keys for:
  - YouTube Data API (`YOUTUBE_API_KEY`)
  - Groq API (`GROQ_API_KEY`)
  - Webshare proxy (optional, `PROXY_USERNAME` and `PROXY_PASSWORD`)
- FFmpeg (for audio playback on some systems)

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd <repository-name>
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Create a `.env` file in the root directory with your API keys:
   ```
   YOUTUBE_API_KEY=your_youtube_api_key
   GROQ_API_KEY=your_groq_api_key
   PROXY_USERNAME=your_proxy_username
   PROXY_PASSWORD=your_proxy_password
   ```
4. Run the FastAPI server:
   ```bash
   uvicorn main:app --reload
   ```
5. Access the app at `http://127.0.0.1:8000`.

## Dependencies

- **FastAPI**: Web framework for building the API and serving static files.
- **google-api-python-client**: Interacts with the YouTube Data API to search for videos.
- **youtube_transcript_api**: Extracts transcripts from YouTube videos, with proxy support via `WebshareProxyConfig`.
- **gTTS**: Converts text summaries to speech.
- **groq**: Interfaces with Grok's AI model for summarization and sentiment analysis.
- **python-dotenv**: Loads environment variables from a `.env` file.
- **json**: Parses tool call arguments from Grok's responses.

## Key Functions

### `main.py`

- **`get_form()`**: Serves the HTML form at the root endpoint (`GET /`).
- **`summarize()`**: Handles `POST /api/summarize`, processes the query, and returns the summary, sentiment, and metadata.
- **`play_audio()`**: Serves the generated `summary.mp3` file (`GET /play_audio`).

### `summarizer.py`

- **`search_youtube_video(query)`**: Searches YouTube for a video matching the query and returns its URL and thumbnail.
- **`extract_transcript(video_url)`**: Extracts the transcript from a YouTube video, limiting it to 16,000 characters if necessary.
- **`summarize(transcript, style)`**: Generates a detailed summary of the transcript in the specified style using Grok's AI.
- **`analyze_sentiment(transcript)`**: Performs a detailed sentiment analysis of the transcript.
- **`process_with_tools(transcript, style)`**: Orchestrates summarization and sentiment analysis using Grok's tool-calling feature, with fallbacks if tools fail.
- **`text_to_speech(summary, output_file)`**: Converts the summary to an MP3 file using gTTS and plays it.
- **`summarize_youtube_video(query, summary_style, tts_enabled)`**: Main function that ties everything together, returning a dictionary with results.

## Tools

The app defines two Grok tools:

1. **`summarize`**: Takes a transcript and style, producing a 500+ word summary.
2. **`analyze_sentiment`**: Takes a transcript and returns a 250+ word sentiment analysis.

These tools are invoked automatically by Grok's `llama-3.3-70b-versatile` model via the `tool_choice="auto"` setting.

## File Structure

```
├── main.py              # FastAPI app entry point
├── summarizer.py        # Core summarization and processing logic
├── templates/           # HTML templates
│   └── index.html       # Web form
├── static/              # Static files (e.g., CSS, JS)
├── summary.mp3          # Generated audio file (temporary)
├── .env                 # Environment variables (not tracked)
└── requirements.txt     # Python dependencies
```

## Usage Example

1. Visit `http://127.0.0.1:8000`.
2. Enter a query (e.g., "Python tutorial"), select a style (e.g., "detailed"), and choose whether to enable TTS.
3. Submit the form to receive a JSON response with the summary, sentiment, video URL, and thumbnail URL.
4. If TTS is enabled, the summary will be played as audio.

## Notes

- The app limits transcripts to 16,000 characters to avoid API token limits.
- Proxy settings are optional but recommended for reliable transcript extraction.
- Summaries and sentiment analyses are designed to be verbose and detailed for maximum insight.
