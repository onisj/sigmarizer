import os
from googleapiclient.discovery import build
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.proxies import WebshareProxyConfig
from gtts import gTTS
from groq import Groq
import json
from dotenv import load_dotenv

load_dotenv()

# SIGMARIZE YOUTUBE: Using Groq tool calling with llama-3.3-70b-versatile for detailed outputs
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
PROXY_USERNAME = os.getenv("PROXY_USERNAME")
PROXY_PASSWORD = os.getenv("PROXY_PASSWORD")


youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)
groq_client = Groq(api_key=GROQ_API_KEY)
ytt_api = YouTubeTranscriptApi(
    proxy_config=WebshareProxyConfig(
        proxy_username=PROXY_USERNAME,
        proxy_password=PROXY_PASSWORD,
    )
)


def search_youtube_video(query):
    try:
        request = youtube.search().list(part="snippet", maxResults=1, q=query, type="video")
        response = request.execute()
        if response["items"]:
            video_id = response["items"][0]["id"]["videoId"]
            thumbnail_url = response["items"][0]["snippet"]["thumbnails"]["high"]["url"]
            print(f"Thumbnail URL: {thumbnail_url}")
            return f"https://www.youtube.com/watch?v={video_id}", thumbnail_url
        return None, None
    except Exception as e:
        print(f"Error searching YouTube: {e}")
        return None, None


def extract_transcript(video_url):
    try:
        video_id = video_url.split("v=")[1]
        transcript = ytt_api.get_transcript(video_id)
        # transcript = ytt_api.fetch(video_id)
        full_text = " ".join([entry["text"] for entry in transcript])
        return full_text[:16000] if len(full_text) > 16000 else full_text
    except Exception as e:
        print(f"Transcript unavailable: {e}")
        return None


def summarize(transcript: str, style: str) -> str:
    messages = [
        {
            "role": "system",
            "content": "You are an expert assistant for summarizing YouTube videos"
                    "Adjust the output length and detail based on the user's requested style: "
                    "'short' (100-200 words for summaries), "
                    "'concise' (200-300 words for summaries), "
                    "or 'detailed' (500+ words for summaries). "
                    "Default to 'concise' if no style is specified."
        },
        {
            "role": "user",
            "content": f"Process this transcript in {style} style: {transcript[:1000]}..."
        }
    ]
    response = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=messages,
        max_tokens=2000,  # Increased for detail
        temperature=0.7
    )
    return response.choices[0].message.content

# def summarize(transcript: str, style: str) -> str:
#     prompt = (
#         f"Generate a highly detailed summary of this YouTube transcript in a {style} style. "
#         f"Include all key points, main ideas, specific examples, accurate names, plot twists, and the overall tone. "
#         f"Ensure the summary is comprehensive, engaging, and at least 600 words long: {transcript}"
#     )
#     response = groq_client.chat.completions.create(
#         model="llama-3.3-70b-versatile",
#         messages=[{"role": "user", "content": prompt}],
#         max_tokens=2000,  # Increased for detail
#         temperature=0.7
#     )
#     return response.choices[0].message.content


def analyze_sentiment(transcript: str, style: str) -> str:
    messages = [
        {
            "role": "system",
            "content": "You are an expert assistant for analyzing sentiment of YouTube videos  "
                    "Adjust the output length and detail based on the user's requested style: "
                    "'short' (50-100 words for sentiment analyses), "
                    "'concise' (100-150 words for sentiment analyses), "
                    "or 'detailed' (250+ words for sentiment analyses). "
                    "Default to 'concise' if no style is specified."
        },
        {
            "role": "user",
            "content": f"Process this transcript in {style} style: {transcript[:1000]}..."
        }
    ]
    response = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=messages,
        max_tokens=2000,  # Increased for detail
        temperature=0.7
    )
    return response.choices[0].message.content
# def analyze_sentiment(transcript: str) -> str:
#     prompt = (
#         f"Perform a detailed sentiment analysis of this YouTube transcript. Include: "
#         f"1) Overall sentiment (positive, negative, neutral) with detailed reasoning, "
#         f"2) Specific emotions detected (e.g., excitement, frustration, curiosity) with their intensity (low, moderate, high) and examples, "
#         f"3) Key phrases or moments driving the sentiment, with thorough context. "
#         f"Return a comprehensive paragraph of at least 250 words: {transcript}"
#     )
#     response = groq_client.chat.completions.create(
#         model="llama-3.3-70b-versatile",
#         messages=[{"role": "user", "content": prompt}],
#         max_tokens=2000,  # Increased for detail
#         temperature=0.7
#     )
#     return response.choices[0].message.content


tools = [
    {
        "type": "function",
        "function": {
            "name": "summarize",
            "description": "Generate a detailed summary of a YouTube transcript in a specified style",
            "parameters": {
                "type": "object",
                "properties": {
                    "transcript": {"type": "string", "description": "The transcript text"},
                    "style": {"type": "string", "enum": ["short", "concise", "detailed"]}
                },
                "required": ["transcript", "style"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "analyze_sentiment",
            "description": "Analyze the sentiment of a YouTube transcript with detailed insights",
            "parameters": {
                "type": "object",
                "properties": {
                    "transcript": {"type": "string", "description": "The transcript text"}
                },
                "required": ["transcript"]
            }
        }
    }
]


def process_with_tools(transcript, style):
    if not transcript:
        return "No transcript available.", "Sentiment analysis unavailable."

    # Initial call to trigger tools
    messages = [
        {
            "role": "system",
            "content": "You are an expert assistant for summarizing YouTube videos and analyzing sentiment. "
                    "Always use both 'summarize' and 'analyze_sentiment' tools for every transcript. "
                    "Adjust the output length and detail based on the user's requested style: "
                    "'short' (50-100 words for summaries, 50-100 words for sentiment analyses), "
                    "'concise' (200-300 words for summaries, 100-150 words for sentiment analyses), "
                    "or 'detailed' (500+ words for summaries, 250+ words for sentiment analyses). "
                    "Default to 'concise' if no style is specified."
        },
        {
            "role": "user",
            "content": f"Process this transcript in {style} style: {transcript[:1000]}..."
        }
    ]
    response = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=messages,
        tools=tools,
        tool_choice="auto",
        max_tokens=300  # Just for tool triggering
    )

    # print(f"RESPONSE: {response.choices[0].message}")

    summary, sentiment = None, None
    if hasattr(response.choices[0].message, "tool_calls") and response.choices[0].message.tool_calls:
        for tool_call in response.choices[0].message.tool_calls:
            func_name = tool_call.function.name
            args = json.loads(tool_call.function.arguments)

            print(f"Tool called: {func_name} with args: {args}")
            if func_name == "summarize":
                summary = summarize(args["transcript"], args["style"])
            elif func_name == "analyze_sentiment":
                sentiment = analyze_sentiment(args["transcript"])

    # Enforce both tools regardless of tool call success
    if not summary:
        print("Fallback: Manually invoking summarize")
        summary = summarize(transcript, style)
    if not sentiment:
        print("Fallback: Manually invoking analyze_sentiment")
        sentiment = analyze_sentiment(transcript)

    print(f"Summary preview: {summary[:200]}...")
    print(f"Sentiment preview: {sentiment[:200]}...")
    return summary, sentiment


def text_to_speech(summary, output_file="summary1.mp3"):
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
    # summary, sentiment = process_with_tools(transcript, summary_style)
    if not transcript:
        summary = "No transcript available."
        sentiment = "Sentiment analysis unavailable."
    else:
        summary = summarize(transcript, summary_style)
        sentiment = analyze_sentiment(transcript, summary_style)

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
