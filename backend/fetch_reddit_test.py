import os
import praw
from dotenv import load_dotenv

load_dotenv()

reddit = praw.Reddit(
    client_id=os.getenv("REDDIT_CLIENT_ID"),
    client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
    user_agent=os.getenv("REDDIT_USER_AGENT"),
)

subreddit = reddit.subreddit("technology")          # or "technology", "apple", etc.
for post in subreddit.new(limit=10):
    print(f"{post.title}  |  {post.selftext[:100]}")