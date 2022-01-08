from typing import List, Union

from card import Card


class Player:
    def __init__(self, id: int) -> None:
        self._id: int = id
        self._no_cards: int = 0 # TODO: Probably not needed?
        self._cards_won: List[int] = []
        self._total_score: int = 0
        self._round_score: int = 0

    def get_id(self) -> int:
        return self._id

    def get_no_cards(self) -> int:
        return self._no_cards

    def update_no_cards(self, no_cards: int) -> None:
        self._no_cards += no_cards

    def update_cards_won(self, card: Union[Card, List[Card]]) -> None:
        if isinstance(card, Card):
            self._cards_won.append(card)            
        else:
            self._cards_won.extend(card)

    # TODO: Change to count_score at the end of game
    def update_score(self, score: int) -> None:
        self._total_score += score

    def reset_player(self) -> None:
        self._no_cards = 0
        self._round_score = 0
        self._cards_won = []
