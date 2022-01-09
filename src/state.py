from enum import Enum, unique


@unique
class State(Enum):
    DEALING = "DEALING"
    BIDDING = "BIDDING"
    PLAYING = "PLAYING"
    ENDED = "ENDED"

    def __str__(self):
        return self.value

    def __repr__(self):
        return self.value
