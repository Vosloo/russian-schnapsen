from typing import List, Union

from card import Card
from config import trumps


class Player:
    def __init__(self, id: int) -> None:
        self._id: int = id
        self._no_cards: int = 0  # TODO: Probably not needed?
        self._cards_won: List[int] = []
        self._total_score: int = 0

    def get_id(self) -> int:
        return self._id

    def get_total_score(self) -> int:
        return self._total_score

    def get_no_cards(self) -> int:
        return self._no_cards

    def update_no_cards(self, no_cards: int) -> None:
        self._no_cards += no_cards

    def update_trump_score(self, trump: str) -> None:
        self._total_score += trumps[trump]

    def _update_score(self, card: Union[Card, List[Card]]) -> None:
        if isinstance(card, Card):
            self._total_score += card.get_score()
        else:
            for c in card:
                self._total_score += c.get_score()

    def update_cards_won(self, card: Union[Card, List[Card]]) -> None:
        if isinstance(card, Card):
            self._cards_won.append(card)
        else:
            self._cards_won.extend(card)

        self._update_score(card)

    def reset_player(self) -> None:
        self._no_cards = 0
        self._cards_won = []

    def __str__(self) -> str:
        return f"Player {self._id}, score: {self._total_score}"

    def __repr__(self) -> str:
        return self.__str__()