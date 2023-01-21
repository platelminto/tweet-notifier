import json
import logging
from dataclasses import dataclass
from typing import Optional

import requests


def _get_auth() -> dict:
    with open('auth.json') as f:
        auth = json.load(f)['pushover']

    return {
        'token': auth['app_token'],
        'user': auth['user_key'],
    }


def send_messages(messages: list[tuple[str, str]], device: Optional[str] = None) -> None:
    data = _get_auth()

    with requests.Session() as s:
        for msg in messages:
            data['title'] = msg[0]
            data['message'] = msg[1]
            if device:
                data['device'] = device

            response = s.post('https://api.pushover.net/1/messages.json', data=data)
            if response.status_code != 200:
                logging.error(f'Pushover API returned {response.status_code} with message: {response.text}')
