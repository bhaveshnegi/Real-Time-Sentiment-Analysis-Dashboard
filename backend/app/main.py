import os, json, asyncio, praw, redis
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from transformers import pipeline
from dotenv import load_dotenv

load_dotenv()

# Reddit client
reddit = praw.Reddit(
    client_id=os.getenv("REDDIT_CLIENT_ID"),
    client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
    user_agent=os.getenv("REDDIT_USER_AGENT"),
)

# Redis
r = redis.Redis(host="redis", port=6379, decode_responses=True)

# Sentiment model
sentiment = pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english")

app = FastAPI()

# ---------- Producer ----------
def fetch_and_push():
    for post in reddit.subreddit("all").new(limit=100):
        payload = {"title": post.title, "body": post.selftext}
        r.lpush("reddit_posts", json.dumps(payload))

# ---------- Consumer ----------
async def process_and_broadcast(websocket: WebSocket):
    await websocket.accept()
    while True:
        _, raw = r.brpop("reddit_posts", timeout=0)
        data = json.loads(raw)
        text = f"{data['title']} {data['body']}"
        result = sentiment(text[:512])[0]  # truncate for speed
        await websocket.send_json({
            "text": text[:100],
            "label": result["label"],
            "score": round(result["score"], 3)
        })

@app.websocket("/ws")
async def ws_endpoint(ws: WebSocket):
    await process_and_broadcast(ws)

# ---------- startup ----------
@app.on_event("startup")
async def startup():
    await asyncio.to_thread(fetch_and_push)  # kick off producer