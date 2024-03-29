import json
import logging
import shelve
from typing import Optional

import requests

from tweet import Tweet, LinkedType

MAX_OLD_TWEETS = 20
MAX_TWEETS_PER_REQUEST = 5


def _get_headers():
    with open("auth.json") as f:
        auth = json.load(f)["twitter"]

    return {
        "Authorization": f'Bearer {auth["bearer"]}',
        "User-Agent": "v2TweetNotifierPython",
    }


def _get(path: str, params: dict = None) -> dict:
    response = requests.get(
        f"https://api.twitter.com/2{path}",
        params=params,
        headers=_get_headers(),
    )

    if response.status_code != 200:
        logging.error(f"Error getting {path}: {response.status_code}. {response.text}")

    return response.json()


def _get_user_info(user_id: str) -> dict:
    with shelve.open("shelf_data") as db:
        user_infos = db.get("user_infos", {})

        if user_id not in user_infos:
            response = _get(f"/users/{user_id}")
            user_infos[user_id] = response["data"]

            db["user_info"] = user_infos

        return user_infos[user_id]


def _get_user_ids(users: list[str]) -> list[str]:
    with shelve.open("shelf_data") as db:
        user_ids = db.get("user_ids", {})
        new_users = [user for user in users if user.lower() not in user_ids]

        if new_users:
            response = _get(
                "/users/by",
                params={"usernames": ",".join(new_users)},
            )
            data = response["data"]

            for user_data in data:
                user_ids[user_data["username"].lower()] = user_data["id"]

            db["user_ids"] = user_ids

        return [str(user_ids[user.lower()]) for user in users]


def _get_tweet_from_data(
    tweet_data: dict, author_data: Optional[dict] = None, linked_tweet_data: Optional[dict] = None
) -> Tweet:
    if author_data is None:
        author_data = {}

    tweet = {
        "content": tweet_data["text"],
        "tweet_id": tweet_data["id"],
        "name": author_data.get("name"),
        "username": author_data.get("username"),
        "linked": None,
        "linked_type": None,
    }

    if linked_tweet_data:
        tweet["linked"] = _get_tweet_from_data(linked_tweet_data, _get_user_info(linked_tweet_data["author_id"]))

        linked_type = tweet_data["referenced_tweets"][0]["type"]
        if linked_type == "retweeted":
            tweet["content"] = None
            tweet["linked_type"] = LinkedType.RETWEET
        elif linked_type == "quoted":
            tweet["linked_type"] = LinkedType.QUOTE
        elif linked_type == "replied_to":
            tweet["linked_type"] = LinkedType.REPLIED_TO

    return Tweet(**tweet)


def _get_tweets_from_response(response_data: dict) -> list[Tweet]:
    data = response_data["data"]
    includes = response_data["includes"]

    tweets = []
    for tweet_data in data:
        linked_tweet_data = None
        if "referenced_tweets" in tweet_data:
            linked_id = tweet_data["referenced_tweets"][0]["id"]
            linked_tweet_data = next((t for t in includes["tweets"] if t["id"] == linked_id), None)

        tweet = _get_tweet_from_data(tweet_data, includes["users"][0], linked_tweet_data)
        tweets.append(tweet)

    return tweets


def _get_latest_user_tweets(user_id: str, pagination_token: Optional[str] = None, calls=0) -> list[Tweet]:
    with shelve.open("shelf_data") as db:
        latest_tweet_ids = db.get("latest_tweet_ids", {})
        latest_tweet_id = latest_tweet_ids.get(user_id)

        skip_rest = False
        params = {
            "expansions": "author_id,referenced_tweets.id",
            "max_results": MAX_TWEETS_PER_REQUEST,
        }

        # Only add the since_id and pagination_token parameters if we haven't reached the max number of tweets.
        # If we have, we can skip to newest tweets.
        if calls * MAX_TWEETS_PER_REQUEST < MAX_OLD_TWEETS:
            params["since_id"] = latest_tweet_id
            params["pagination_token"] = pagination_token
        else:
            skip_rest = True

        # This request returns newest tweets first, and pagination goes backwards in time.
        response = _get(
            f"/users/{user_id}/tweets",
            params=params,
        )

        if "data" not in response:
            return []

        meta = response["meta"]
        pagination_next_token = meta.get("next_token")

        tweets = _get_tweets_from_response(response)
        if pagination_next_token and not skip_rest:
            tweets += _get_latest_user_tweets(user_id, pagination_next_token, calls + 1)

        latest_tweet_ids[user_id] = response["data"][0]["id"]  # change for testing
        db["latest_tweet_ids"] = latest_tweet_ids

        # If the latest tweet wasn't specified (i.e. first time running), return the first few tweets.
        if not latest_tweet_id:
            return tweets[:3]

        return tweets


def get_latest_tweets(users: list[str]) -> list[Tweet]:
    user_ids = _get_user_ids(users)

    result = []
    for user_id in user_ids:
        result.extend(_get_latest_user_tweets(user_id))
    return result
