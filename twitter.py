import json
from dataclasses import dataclass
from typing import Self, Optional

import requests


@dataclass
class Tweet:
    content: str
    created_at: str
    id: int
    author_name: str
    author_handle: str
    linked = Optional[Self]

    @property
    def title(self):
        if self.linked:
            return f'{self.author_name} linked {self.linked.author_name}\'s tweet'

        return f'{self.author_name} tweeted'

    @property
    def message(self):
        if self.linked:
            if self.content:
                return f'''{self.content}
                
                {self.linked.author_handle}: "{self.linked.content}"'''

            return f'{self.linked.author_handle}: "{self.linked.content}"'

        return self.content


def get_latest_tweets(user: str) -> list[Tweet]:
    url = f'https://api.twitter.com/2/users/by/username/{user}?user.fields=created_at'
    response = requests.get(url)


with open('auth.json') as f:
    config = json.load(f)

