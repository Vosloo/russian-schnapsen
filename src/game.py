from typing import List, Union, Set

import pandas as pd

from card import Card
from player import Player
from state import State

NAME = "name"


class Game:
    def __init__(self) -> None:
        self._state: Union[State, None] = None
        self._no_players: int = 3
        self._round_starting_player: int = -1
        self._cards_played: Set[Card] = set()
        self._cards_in_round: List[Card] = []

        self.current_trump: Union[str, None] = None

        self.players: List[Player] = self._initialize_players()
        self.winner: Union[Player, None] = None

    def check_points(self) -> bool:
        for player in self.players:
            if player.get_total_score() >= 1000:
                self._state = State.ENDED
                return player

        return None

    def reset_round(self) -> None:
        for player in self.players:
            player.reset_player()

        self._cards_played = set()
        self._round_starting_player = -1
        self._state = State.DEALING

    def get_current_player(self) -> int:
        return self._round_starting_player

    def get_no_players(self) -> int:
        return self._no_players

    def get_state(self) -> State:
        return self._state.value

    def run_game(self) -> Player:
        while self._state is not State.ENDED:
            self.reset_round()
            self._state = self._run_round()

        return self.winner

    def _run_round(self) -> State:
        self._state = State.DEALING
        self._deal_cards()
        self._state = State.STOCK
        self._bid_stock()
        self._state = State.PLAYING
        self._play_cards()

        if (player := self.check_points()) is not None:
            self.winner = player

        return self._state

    def _update_played_cards(self, detected_set: set) -> None:
        self._cards_played.update(detected_set)

    def set_state(self, state: State) -> None:
        self._state = state

    def _initialize_players(self) -> List[Player]:
        players = []
        for player_id in range(0, self._no_players):
            players.append(Player(player_id))

    def _load_played_cards(self):
        if len(self._cards_in_round) > self._no_players:
            # Detected trump cards
            ...
        elif len(self._cards_in_round) == self._no_players:
            if self.current_trump is not None:
                ...
            else:
                pivot_card = None
                winning_player = None
                for ind, card in enumerate(self._cards_in_round):
                    if ind == 0:
                        pivot_card = card
                        winning_player = self.players[self._round_starting_player]
                    else:
                        if (
                            card.get_suit() == pivot_card.get_suit()
                            and card > pivot_card
                        ):
                            pivot_card = card
                            winning_player = self.players[
                                (self._round_starting_player + ind) % self._no_players
                            ]

                winning_player.update_cards_won(self._cards_in_round)

        else:
            raise Exception("Not enough cards in round!")

    def game_frame(self, detected_cards: pd.DataFrame):
        if self._state == State.DEALING:
            ...
        elif self._state == State.STOCK:
            ...
        elif self._state == State.PLAYING:
            if not len(detected_cards[NAME].iloc[0]):
                self._load_played_cards()

            # Getting cards that entered in given frame
            # TODO: what if card edges are labeled differently
            detected_set = set([detected_cards[NAME].iloc[0]])
            entering_card: set = detected_set - self._cards_played

            if not entering_card:
                ...

            self._cards_in_round.append(Card(entering_card.pop()))

        elif self._state == State.ENDED:
            ...
