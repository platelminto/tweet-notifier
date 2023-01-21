from dataclasses import dataclass
from enum import Enum
from typing import Optional, Self


class LinkedType(Enum):
    RETWEET = "retweeted"
    QUOTE = "quoted"
    REPLIED_TO = "replied to"


@dataclass()
class Tweet:
    content: Optional[str]
    tweet_id: int
    name: Optional[str]
    username: Optional[str]
    linked: Optional[Self]
    linked_type: Optional[LinkedType]

    @property
    def title(self):
        if self.linked:
            return f"{self.name} {self.linked_type.value} {self.linked.name}'s tweet"

        return f"{self.name} tweeted"

    @property
    def message(self):
        if self.linked:
            if self.content:
                return f'''\
{self.content}

{self.linked_type.name}:
@{self.linked.username}: "{self.linked.content}"'''

            return f'{self.linked.username}: "{self.linked.content}"'
        return self.content
