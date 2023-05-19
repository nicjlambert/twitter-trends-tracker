from flask import Flask, jsonify, render_template
import tweepy
import os

app = Flask(__name__)

def authenticate_twitter_app():

    consumer_key = os.getenv('TWITTER_CONSUMER_KEY')
    consumer_secret = os.getenv('TWITTER_CONSUMER_SECRET')
    access_token = os.getenv('TWITTER_ACCESS_TOKEN')
    access_token_secret = os.getenv('TWITTER_ACCESS_TOKEN_SECRET')

    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)

    api = tweepy.API(auth)
    return api

@app.route('/trends', methods=['GET'])
def get_trends():
    api = authenticate_twitter_app()

    # Try to authenticate
    try:
        api.verify_credentials()
    except Exception as e:
        return jsonify({"error": "Authentication failed!", "details": str(e)})

    # Get the trending tweets in Canberra
    try:
        trends = api.get_place_trends("1100661")
    except Exception as e:
        return jsonify({"error": "Failed to fetch trends!", "details": str(e)})
    
    # Return the trending tweets
    trending_tweets = [{'name': trend['name'], 'url': trend['url'], 'tweet_volume': trend['tweet_volume'] or 0} for trend in trends[0]['trends']]
    return jsonify({"trending_tweets": trending_tweets})

@app.route('/trends_chart', methods=['GET'])
def trends_chart():
    api = authenticate_twitter_app()
    trends = api.get_place_trends("1100661")

    # Prepare data for the chart
    data = [{'name': trend['name'], 'volume': trend['tweet_volume'] or 0} for trend in trends[0]['trends']]  # Some tweet volumes might be None, so replace with 0

    # Render the template with the data
    return render_template('trends_chart.html', data=data)


if __name__ == '__main__':
    app.run(debug=True)
