import os
from googleapiclient.discovery import build
from youtube_transcript_api import YouTubeTranscriptApi
from gtts import gTTS
from langchain.prompts import PromptTemplate
from groq import Groq
import time

# SIGMARIZE YOUTUBE: A tool to summarize YouTube videos with sentiment analysis
# API Keys
YOUTUBE_API_KEY =  "AIzaSyB9ALcT6eNswl19gYtw3fbaHmJXsKR2HdQ"
GROQ_API_KEY =  "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"

youtube = build("youtube", "v3", developerKey="AIzaSyB9ALcT6eNswl19gYtw3fbaHmJXsKR2HdQ")
groq_client = Groq(api_key="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")

# Dynamic Summary Prompt for SIGMARIZE YOUTUBE
summary_prompt_template = PromptTemplate(
    input_variables=["transcript", "style"],
    template="Summarize the following YouTube video transcript in a {style} way, capturing the key points, main ideas, and overall tone: {transcript}"
)

# Fine-Tuned Sentiment Prompt for SIGMARIZE YOUTUBE
sentiment_prompt = PromptTemplate(
    input_variables=["transcript"],
    template="Analyze the sentiment of this YouTube video transcript in detail. Provide: 1) The overall sentiment (positive, negative, or neutral), 2) Specific emotions detected (e.g., excitement, frustration, curiosity) with their intensity (low, moderate, high), 3) Key phrases or moments that contribute to the sentiment, including timestamps or context if applicable. Return the response in a concise paragraph: {transcript}"
)

def search_youtube_video(query):
    try:
        request = youtube.search().list(part="snippet", maxResults=1, q=query, type="video")
        response = request.execute()
        if response["items"]:
            video_id = response["items"][0]["id"]["videoId"]
            return f"https://www.youtube.com/watch?v={video_id}"
        return None
    except Exception as e:
        print(f"Error searching YouTube: {e}")
        return None

def extract_transcript(video_url):
    try:
        video_id = video_url.split("v=")[1]
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        return " ".join([entry["text"] for entry in transcript])
    except Exception as e:
        print(f"Transcript unavailable: {e}")
        return None

def estimate_tokens(text):
    """Roughly estimate token count (1 token ≈ 4 characters)."""
    return len(text) // 4

def split_transcript(transcript, max_tokens=4000):
    """Split transcript into chunks under max_tokens for SIGMARIZE YOUTUBE."""
    words = transcript.split()
    chunks = []
    current_chunk = []
    current_tokens = 0

    for word in words:
        word_tokens = estimate_tokens(word) + 1  # +1 for space
        if current_tokens + word_tokens > max_tokens:
            chunks.append(" ".join(current_chunk))
            current_chunk = [word]
            current_tokens = word_tokens
        else:
            current_chunk.append(word)
            current_tokens += word_tokens
    
    if current_chunk:
        chunks.append(" ".join(current_chunk))
    
    return chunks

def call_groq(prompt):
    if not isinstance(prompt, str):
        print(f"Invalid prompt type: {type(prompt)}. Converting to string.")
        prompt = str(prompt) if prompt is not None else "No content provided."
    
    try:
        response = groq_client.chat.completions.create(
            model="mixtral-8x7b-32768",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=200
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Groq API error: {e}")
        return f"Error calling Groq API: {e}"

def generate_summary(transcript, summary_style="concise"):
    if not transcript:
        return "No transcript available to summarize."
    
    from langchain_core.runnables import RunnableLambda
    summary_chain = summary_prompt_template | RunnableLambda(lambda x: call_groq(x))
    
    total_tokens = estimate_tokens(transcript)
    if total_tokens > 4000:
        chunks = split_transcript(transcript)
        summaries = []
        for chunk in chunks:
            summary = summary_chain.invoke({"transcript": chunk, "style": summary_style})
            summaries.append(summary)
            time.sleep(1)
        return " ".join(summaries)
    else:
        return summary_chain.invoke({"transcript": transcript, "style": summary_style})

def analyze_sentiment(transcript):
    if not transcript:
        return "Sentiment analysis unavailable due to missing transcript."
    
    from langchain_core.runnables import RunnableLambda
    sentiment_chain = sentiment_prompt | RunnableLambda(lambda x: call_groq(x))
    
    total_tokens = estimate_tokens(transcript)
    if total_tokens > 4000:
        chunks = split_transcript(transcript)
        sentiments = []
        for chunk in chunks:
            sentiment = sentiment_chain.invoke({"transcript": chunk})
            sentiments.append(sentiment)
            time.sleep(1)
        return " ".join(sentiments)
    else:
        return sentiment_chain.invoke({"transcript": transcript})

def text_to_speech(text, sentiment, output_file="summary.mp3"):
    try:
        full_text = f"Summary: {text}. Sentiment Analysis: {sentiment}"
        tts = gTTS(text=full_text, lang="en")
        tts.save(output_file)
        os.system(f"start {output_file}")
    except Exception as e:
        print(f"Error with TTS: {e}")

def summarize_youtube_video(query, summary_style="concise", tts_enabled=False):
    video_url = search_youtube_video(query)
    if not video_url:
        return {"summary": "Video not found.", "video_url": None, "sentiment": "No sentiment analysis possible."}
    
    transcript = extract_transcript(video_url)
    summary = generate_summary(transcript, summary_style=summary_style)
    sentiment = analyze_sentiment(transcript)
    
    if tts_enabled:
        text_to_speech(summary, sentiment)
    
    return {"summary": summary, "video_url": video_url, "sentiment": sentiment}