import json

with open('config.json') as f:
    config = json.load(f)

users = config['users']

for user in users:
    tweets = get_latest_tweets(user)
