import json

from twitter import get_latest_tweets


if __name__ == '__main__':
    with open('config.json') as f:
        config = json.load(f)

    users = config['users']

    tweets = get_latest_tweets(users)

    for t in tweets:
        print(t.title)
        print(t.message)
        print()
