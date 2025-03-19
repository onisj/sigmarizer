import os
from googleapiclient.discovery import build
from youtube_transcript_api import YouTubeTranscriptApi
from gtts import gTTS
from groq import Groq

# SIGMARIZE YOUTUBE: Using llama-3.3-70b-versatile with detailed prompts and thumbnails
YOUTUBE_API_KEY = "YOUTUBE API "
GROQ_API_KEY = "groq api"

youtube = build("youtube", "v3", developerKey= "YOUTUBE API")
groq_client = Groq(api_key= "GROQ API KEY"
)

def search_youtube_video(query):
    try:
        request = youtube.search().list(part="snippet", maxResults=1, q=query, type="video")
        response = request.execute()
        if response["items"]:
            video_id = response["items"][0]["id"]["videoId"]
            thumbnail_url = response["items"][0]["snippet"]["thumbnails"]["high"]["url"]
            print(f"Thumbnail URL: {thumbnail_url}")  # Debug
            return f"https://www.youtube.com/watch?v={video_id}", thumbnail_url
        return None, None
    except Exception as e:
        print(f"Error searching YouTube: {e}")
        return None, None

def extract_transcript(video_url):
    try:
        video_id = video_url.split("v=")[1]
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        full_text = " ".join([entry["text"] for entry in transcript])
        return full_text[:16000] if len(full_text) > 16000 else full_text
    except Exception as e:
        print(f"Transcript unavailable: {e}")
        return None

def call_groq(prompt):
    try:
        response = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",  
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1000,  # Increased for detail
            temperature=0.7  # Balanced creativity and coherence
        )
        content = response.choices[0].message.content
        print(f"Groq response: {content[:200]}...")  
        return content
    except Exception as e:
        print(f"Groq API error: {e}")
        return f"Error: {e}"

def generate_summary(transcript, style="concise"):
    if not transcript:
        return "No transcript available to summarize."
    prompt = (
        f"Provide a detailed summary of the following YouTube video transcript in a {style} style. "
        f"Include key points, main ideas, overall tone, and specific examples where relevant. "
        f"provide accurate names and plot twist. "
        f"Make it comprehensive and engaging: {transcript}"
    )
    return call_groq(prompt)

def analyze_sentiment(transcript):
    if not transcript:
        return "Sentiment analysis unavailable due to missing transcript."
    prompt = (
        f"Analyze the sentiment of this YouTube video transcript in detail. Provide: "
        f"1) The overall sentiment (positive, negative, or neutral), "
        f"2) Specific emotions detected (e.g., excitement, frustration, curiosity) with their intensity (low, moderate, high), "
        f"3) Key phrases or moments that contribute to the sentiment, including context if possible. "
        f"Return a concise yet detailed paragraph: {transcript}"
    )
    return call_groq(prompt)

def text_to_speech(summary, output_file="summary.mp3"):
    try:
        tts = gTTS(text=f"Summary: {summary}", lang="en")
        tts.save(output_file)
        os.system(f"start {output_file}")
    except Exception as e:
        print(f"Error with TTS: {e}")

def summarize_youtube_video(query, summary_style="concise", tts_enabled=False):
    video_url, thumbnail_url = search_youtube_video(query)
    if not video_url:
        return {"summary": "Video not found.", "video_url": None, "sentiment": "No sentiment analysis possible.", "thumbnail_url": None}
    
    transcript = extract_transcript(video_url)
    summary = generate_summary(transcript, summary_style)
    sentiment = analyze_sentiment(transcript)
    
    if tts_enabled:
        text_to_speech(summary)
    
    result = {
        "summary": summary,
        "video_url": video_url,
        "sentiment": sentiment,
        "thumbnail_url": thumbnail_url
    }
    print(f"Result: {result}")  
    return result