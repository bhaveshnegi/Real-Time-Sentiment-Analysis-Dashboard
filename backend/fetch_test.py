import os, tweepy
from dotenv import load_dotenv
load_dotenv()

client = tweepy.Client(bearer_token=os.getenv("TWITTER_BEARER_TOKEN"))

query = "iPhone 15 -is:retweet lang:en"
tweets = client.search_recent_tweets(query=query, max_results=10)

for t in tweets.data:
    print(t.text)