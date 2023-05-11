from flask import Flask
import tweepy
import re
from summarizer import Summarizer
import threading

app = Flask(__name__)

# Replace with your own Twitter API keys and access tokens
API_KEY = 'your_api_key'
API_SECRET = 'your_api_secret'
ACCESS_TOKEN = 'your_access_token'
ACCESS_TOKEN_SECRET = 'your_access_token_secret'

# Authenticate with Twitter API
auth = tweepy.OAuthHandler(API_KEY, API_SECRET)
auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

# Function to clean text
def clean_text(text):
    text = re.sub(r"http\S+|www\S+|https\S+", "", text, flags=re.MULTILINE)
    text = re.sub(r'\@\w+|\#', "", text)
    text = text.strip().lower()
    return text

# Function to fetch trending topics and summarize them
def summarize_trends():
    summarizer = Summarizer()
    trending = api.get_place_trends(id=1)  # Fetch trending topics worldwide (WOEID 1)
    trends = [trend['name'] for trend in trending[0]['trends']]

    for trend in trends:
        print(f"Summarizing trend: {trend}")
        tweets = []
        try:
            for tweet in tweepy.Cursor(api.search_tweets, q=trend, lang="en", tweet_mode="extended").items(100):
                tweets.append(clean_text(tweet.full_text))
        except tweepy.TweepError as e:
            print(f"Error fetching tweets for trend {trend}: {e}")

        # Summarize the tweets and post it
        if tweets:
            summarized_text = summarizer(" ".join(tweets), max_length=50)
            if not summarized_text:
                summarized_text = f"Couldn't summarize {trend}. Check the trend for more information."
            else:
                summarized_text = summarized_text[:280]
            api.update_status(f"Summary of {trend}: {summarized_text}")

@app.route('/start', methods=['GET'])
def start():
    thread = threading.Thread(target=summarize_trends)
    thread.start()
    return "Started summarizing trends!"

if __name__ == "__main__":
    app.run(port=5000)
