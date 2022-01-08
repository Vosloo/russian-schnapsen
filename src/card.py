from config import scores


class Card:
    def __init__(self, card_class: str) -> None:
        self._card_class: str = card_class
        self._value, self._suit = card_class[:-1], card_class[-1]
        self._score = self._get_points()

    def get_name(self):
        return self._card_class

    def _get_points(self):
        return scores[self._value]

    def get_score(self):
        return self._score

    def get_value(self):
        return self._value

    def get_suit(self):
        return self._suit

    def is_queen(self):
        return self._value == "Q"

    def is_king(self):
        return self._value == "K"

    def __str__(self):
        return self.get_name()

    def __repr__(self):
        return self.get_name()

    def __eq__(self, other: "Card"):
        return self._score == other.get_score()

    def __lt__(self, other: "Card"):
        return self._score < other.get_score()

    def __gt__(self, other: "Card"):
        return self._score > other.get_score()


if __name__ == "__main__":
    c = Card("JH")
    print(c.get_score())

    c = Card("10S")
    print(c.get_score())

    c = Card("AC")
    print(c.get_score())
