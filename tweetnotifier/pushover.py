import json
import logging
from typing import Optional

import requests

from tweet import Tweet


def _get_auth() -> dict:
    with open("auth.json") as f:
        auth = json.load(f)["pushover"]

    return {
        "token": auth["app_token"],
        "user": auth["user_key"],
    }


def send_messages(data: list[dict], device: Optional[str] = None) -> None:
    auth = _get_auth()

    with requests.Session() as s:
        for message_data in data:
            message_data.update(auth)

            if device:
                message_data["device"] = device

            response = s.post("https://api.pushover.net/1/messages.json", data=message_data)
            if response.status_code != 200:
                logging.error(f"Pushover API returned {response.status_code} with message: {response.text}")


def send_tweets(tweets: list[Tweet], device: Optional[str] = None) -> None:
    data = []
    for tweet in tweets:
        message_data = {
            "title": tweet.title,
            "message": tweet.message,
            "url": f"https://twitter.com/{tweet.username}/status/{tweet.tweet_id}",
            "url_title": "View on Twitter",
        }

        data.append(message_data)

    send_messages(data, device)
