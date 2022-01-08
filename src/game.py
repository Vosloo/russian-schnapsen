from typing import List, Union, Set

import pandas as pd
import numpy as np

from card import Card
from player import Player
from state import State

NAME = "name"
CONFIDENCE = "confidence"


class Game:
    def __init__(self, verbose) -> None:
        self._state: State = State.DEALING
        self._no_players: int = 3
        self._verbose = verbose

        self.players: List[Player] = self._initialize_players()
        self.winner: Union[Player, None] = None

        self._cards_played: Set[str] = set()
        self.current_trump: Union[str, None] = None

        self._round_starting_player: int = -1
        self._cards_in_round: List[Card] = []

    def check_points(self) -> bool:
        for player in self.players:
            if player.get_total_score() >= 1000:
                return player

        return None

    def _print_player_scores(self) -> None:
        for player in self.players:
            print(player)

    def _reset_round(self) -> None:
        for player in self.players:
            player.reset_player()

        self._cards_in_round = []
        self._round_starting_player = -1
        self._state = State.DEALING

    def get_current_player(self) -> int:
        return self._round_starting_player

    def get_no_players(self) -> int:
        return self._no_players

    def get_state(self) -> State:
        return self._state

    def _update_played_cards(self, detected_card: str) -> None:
        self._cards_played.update({detected_card})

    def set_state(self, state: State) -> None:
        self._state = state

    def _initialize_players(self) -> List[Player]:
        players = []
        for player_id in range(0, self._no_players):
            players.append(Player(player_id))

        return players

    def _update_winning_player(
        self, ind: int, card: Card, winning_player: Player, pivot_card: Card
    ) -> Union[Player, Card]:
        # print(f"Ind: {ind} Card: {card} Pivot: {pivot_card}")
        if ind == 0:
            # print("First card, setting as pivot")
            pivot_card = card
            winning_player = self.players[self._round_starting_player]
        elif card.get_suit() == pivot_card.get_suit():
            if card > pivot_card:
                # print("Card has the same suit and has bigger value, changing pivot")
                pivot_card = card
                winning_player = self.players[
                    (self._round_starting_player + ind) % self._no_players
                ]
            # else:
            # print("Card has the same suit but has smaller value, skipping")
        # Current trump is not None
        elif card.get_suit() == self.current_trump:
            print("Card has trump suit, changing pivot")
            pivot_card = card
            winning_player = self.players[
                (self._round_starting_player + ind) % self._no_players
            ]

        self._update_played_cards(card.get_name())

        return winning_player, pivot_card

    def _load_played_cards(self):
        if len(self._cards_in_round) > self._no_players:
            print("Detected trump cards")
            # Detected trump cards
            trump_suit = None
            pivot_card = None
            winning_player = None
            for ind, card in enumerate(self._cards_in_round):
                if card.is_queen():
                    print("Card is queen, waiting for king")
                    trump_suit = card.get_suit()
                elif card.is_king() and card.get_suit() == trump_suit:
                    print("Detected king with the same suit, setting trump suit")
                    self.players[
                        (self._round_starting_player + ind) % self._no_players
                    ].update_trump_score(trump_suit)
                    continue
                elif trump_suit is not None:
                    print("Card is not a king, no new trump suit")
                    trump_suit = None

                winning_player, pivot_card = self._update_winning_player(
                    ind, card, winning_player, pivot_card
                )

            winning_player.update_cards_won(self._cards_in_round)
            self._round_starting_player = winning_player.get_id()

        elif len(self._cards_in_round) == self._no_players:
            print("No one has declared new trump")
            pivot_card = None
            winning_player = None
            for ind, card in enumerate(self._cards_in_round):
                winning_player, pivot_card = self._update_winning_player(
                    ind, card, winning_player, pivot_card
                )

            winning_player.update_cards_won(self._cards_in_round)
            self._round_starting_player = winning_player.get_id()
            print(f"Player {winning_player.get_id()} won the round")

        else:
            raise Exception("Not enough cards in round!")

    def game_frame(self, detected_cards: pd.DataFrame):
        if self.get_state() == State.DEALING:
            print("Dealing cards...")
            self.set_state(State.STOCK)
        elif self.get_state() == State.STOCK:
            print("Bidding stock...")
            self._round_starting_player = 0
            print("Starting player:", self._round_starting_player)
            self.set_state(State.PLAYING)
        elif self.get_state() == State.PLAYING:
            if (
                len(self._cards_in_round) >= self._no_players
                and len(detected_cards.index) == 0
            ):
                print("Round ending...")
                self._load_played_cards()
                player_won = self.check_points()
                if player_won is not None:
                    print("Player", player_won.get_id(), "won!")
                    self.winner = player_won
                    self.set_state(State.ENDED)
                else:
                    self._print_player_scores()
                    print("Round reset...")
                    self._reset_round()
                    self.set_state(State.DEALING)
            else:
                # Getting cards that entered in given frame
                # TODO: what if card edges are labeled differently
                detected_set = set(
                    detected_cards[detected_cards[CONFIDENCE] > 0.25][NAME]
                )
                entering_card: set = detected_set - (
                    self._cards_played
                    | set([card.get_name() for card in self._cards_in_round])
                )

                if len(detected_set):
                    print("Detected:", detected_set)
                    print(
                        "In round:",
                        set([card.get_name() for card in self._cards_in_round]),
                    )
                    print("Played:", self._cards_played)
                    print("Entering:", entering_card, "\n")

                detected_cards = (
                    detected_cards[
                        (detected_cards[CONFIDENCE] > 0.25)
                        & (detected_cards[NAME].isin(entering_card))
                    ]
                    .max()
                    .replace({np.nan: None})
                )

                conf, card = detected_cards[CONFIDENCE], detected_cards[NAME]

                if not card:
                    # No new card detected
                    return

                # print("New card in round:", card, '\n\n')
                self._cards_in_round.append(Card(card))

        elif self.get_state() == State.ENDED:
            return self.winner

