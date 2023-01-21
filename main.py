import json

from pushover import Message, send_messages
from twitter import get_latest_tweets


if __name__ == '__main__':
    with open('config.json') as f:
        config = json.load(f)

    users = config['twitter']['users']
    device = config['pushover']['device']

    tweets = get_latest_tweets(users)

    send_messages(
        [Message(tweet.title, tweet.message) for tweet in tweets],
        device
    )
