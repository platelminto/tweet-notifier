import itertools
import json
import shelve
from dataclasses import dataclass

import requests


@dataclass
class Tweet:
    message: str
    id: int
    author_name: str


def _get_headers():
    with open('auth.json') as f:
        auth = json.load(f)

    return {
        'Authorization': f'Bearer {auth["bearer"]}',
        'User-Agent': 'v2TweetNotifsPython',
    }


def _get(path: str, params: dict = None) -> dict:
    response = requests.get(
        f'https://api.twitter.com/2{path}',
        params=params,
        headers=_get_headers(),
    )

    return response.json()['data']


def _get_user_ids(users: list[str]) -> list[str]:
    with shelve.open('shelf_data') as db:
        user_datas = db.get('user_info', {})
        new_users = [user for user in users if user not in user_datas]

        if new_users:
            data = _get(
                '/users/by',
                params={'usernames': ','.join(new_users)},
            )

            for user_data in data:
                username = user_data.pop('username')
                user_datas[username] = user_data

            db['user_ids'] = user_datas

        return [str(user_datas[user]['id']) for user in users]


def _get_latest_user_tweets(user_id: str) -> list[Tweet]:
    with shelve.open('shelf_data') as db:
        latest_tweet_ids = db.get('latest_tweet_ids', {})
        latest_tweet_id = latest_tweet_ids.get(user_id)

        data = _get(
            f'/users/{user_id}/tweets',
            params={'until_id': latest_tweet_id},
        )

        latest_tweet_ids[user_id] = data[0]['id']

        if not latest_tweet_id:
            return []

        return [
            Tweet(
                tweet['text'],
                tweet['id'],
                db['user_info'][user_id]['name'],
            ) for tweet in data]


def get_latest_tweets(users: list[str]) -> list[Tweet]:
    user_ids = _get_user_ids(users)

    # Flatten list
    return list(itertools.chain.from_iterable(
        [_get_latest_user_tweets(user_id) for user_id in user_ids]
    ))
