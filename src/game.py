from typing import List, Union, Set

import pandas as pd
import numpy as np

from card import Card
from player import Player
from state import State
from verboser import Verboser

NAME = "name"
CONFIDENCE = "confidence"
THRESHOLD = 5

BIDDINGS = [[110], [100, 120], []]
NO_CARDS_IN_DECK = 24


class Game:
    def __init__(self, verbose: str) -> None:
        # TODO: Change start state to DEALING
        self._state: State = State.DEALING
        self._no_players: int = 3
        self._verbose: Verboser = Verboser(verbose)

        self.players: List[Player] = self._initialize_players()
        self.winner: Union[Player, None] = None

        self._cards_dealt: Set[str] = set()

        self._cards_played: Set[str] = set()
        self.current_trump: Union[str, None] = None

        # TODO: Change to a player that won the bidding
        self._round_starting_player: int = 0
        self._cards_in_round: List[Card] = []

    def check_points(self) -> bool:
        for player in self.players:
            if player.get_total_score() >= 1000:
                return player

        return None

    def _print_player_scores(self) -> None:
        print()
        for player in self.players:
            print(player)
        print()

    def _reset_round(self, player_won_round: Player) -> None:
        for player in self.players:
            player.reset_player()

        self._cards_in_round = []
        self._round_starting_player = player_won_round.get_id()
        self._state = State.PLAYING

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
            players.append(Player(player_id, BIDDINGS[player_id]))

        return players

    def _update_winning_player(
        self, ind: int, card: Card, winning_player: Player, pivot_card: Card
    ) -> Union[Player, Card]:
        if self._verbose == Verboser.DEBUG:
            print(f"Ind: {ind} Card: {card} Pivot: {pivot_card}")
        if ind == 0:
            if self._verbose == Verboser.DEBUG:
                print("First card, setting as pivot")
            pivot_card = card
            winning_player = self.players[self._round_starting_player]
        elif card.get_suit() == pivot_card.get_suit():
            if card > pivot_card:
                if self._verbose == Verboser.DEBUG:
                    print("Card has the same suit and has bigger value, changing pivot")
                pivot_card = card
                winning_player = self.players[
                    (self._round_starting_player + ind) % self._no_players
                ]
            elif self._verbose == Verboser.DEBUG:
                print("Card has the same suit but has smaller value, skipping")
        # Current trump is not None
        elif card.get_suit() == self.current_trump:
            if self._verbose == Verboser.DEBUG:
                print("Card has trump suit, changing pivot")
            pivot_card = card
            winning_player = self.players[
                (self._round_starting_player + ind) % self._no_players
            ]

        self._update_played_cards(card.get_name())

        return winning_player, pivot_card

    def _load_played_cards(self) -> Player:
        if len(self._cards_in_round) > self._no_players:
            if self._verbose == Verboser.DEBUG:
                print("Detected trump cards")

            trump_suit = None
            pivot_card = None
            winning_player = None
            for ind, card in enumerate(self._cards_in_round):
                if card.is_queen():
                    if self._verbose == Verboser.DEBUG:
                        print("Card is queen, waiting for king")

                    trump_suit = card.get_suit()
                elif card.is_king() and card.get_suit() == trump_suit:
                    if self._verbose == Verboser.DEBUG:
                        print("Detected king with the same suit, setting trump suit")
                    if self._verbose in (Verboser.INFO, Verboser.DEBUG):
                        print("New trump suit:", trump_suit)

                    self.players[
                        (self._round_starting_player + ind - 1) % self._no_players
                    ].update_trump_score(trump_suit)
                    trump_suit = None
                    continue
                elif trump_suit is not None:
                    if self._verbose == Verboser.DEBUG:
                        print("Card is not a king, no new trump suit")

                    trump_suit = None

                winning_player, pivot_card = self._update_winning_player(
                    ind, card, winning_player, pivot_card
                )

            winning_player.update_cards_won(self._cards_in_round)
            # self._round_starting_player = winning_player.get_id()

            return winning_player

        elif len(self._cards_in_round) == self._no_players:
            pivot_card = None
            winning_player = None
            for ind, card in enumerate(self._cards_in_round):
                winning_player, pivot_card = self._update_winning_player(
                    ind, card, winning_player, pivot_card
                )

            winning_player.update_cards_won(self._cards_in_round)
            # self._round_starting_player = winning_player.get_id()
            if self._verbose in (Verboser.INFO, Verboser.DEBUG):
                print(f"\nPlayer {winning_player.get_id()} won the round!")
            
            return winning_player

        else:
            raise Exception("Not enough cards in round!")

    def _get_entering_card(self, detected_cards: pd.DataFrame, dealing=False) -> Union[str, None]:
        detected_set = set(detected_cards[NAME])

        if dealing:
            entering_card: set = detected_set - self._cards_dealt
        else:
            entering_card: set = detected_set - (
                self._cards_played
                | set([card.get_name() for card in self._cards_in_round])
            )

        cut_cards = (
            detected_cards[
                (
                    (detected_cards[NAME].isin(entering_card))
                    & (detected_cards[CONFIDENCE] > 0.25)
                )
            ]
            .groupby(NAME)
            .filter(lambda x: len(x) > THRESHOLD)
        )

        new_card = cut_cards.max().replace({np.nan: None})

        if self._verbose == Verboser.DEBUG:
            print("\nDetected:", detected_set)
            if dealing:
                print("Dealt:", self._cards_dealt)
            else:
                print(
                    "In round:", [card.get_name() for card in self._cards_in_round],
                )
                print("Played in game:", self._cards_played)
            print(f"Entering: {entering_card}\n")

        return new_card[NAME]

    def _dealing_stage(self, detected_cards: pd.DataFrame):
        if self._verbose == Verboser.DEBUG:
            print("Dealing cards...")

        card = self._get_entering_card(detected_cards, dealing=True)
        if card is None:
            # No new card detected
            return

        if self._verbose in (Verboser.INFO, Verboser.DEBUG):
            print("New card:", card)

        self._cards_dealt.update({card})

        if len(self._cards_dealt) == NO_CARDS_IN_DECK:
            self.set_state(State.BIDDING)

    def _bidding_stage(self):
        if self._verbose == Verboser.DEBUG:
            print("Bidding stock...")

        winning_player = None
        winning_bid = 0
        while True:
            bids_left = False
            for player in self.players:
                cur_bidding = player.pop_bidding()
                if cur_bidding != 0:
                    bids_left = True

                if cur_bidding > winning_bid:
                    winning_bid = cur_bidding
                    winning_player = player

            if not bids_left:
                break

        self._round_starting_player = winning_player.get_id()
        if self._verbose in (Verboser.INFO, Verboser.DEBUG):
            print(f"Player {self._round_starting_player}. won the bid with the value {winning_bid}\n")

        self.set_state(State.PLAYING)

    def _playing_stage(self, detected_cards: pd.DataFrame):
        if len(self._cards_in_round) >= self._no_players and detected_cards.empty:
            if self._verbose == Verboser.DEBUG:
                print("\nRound ending, computing scores...")

            player_won_round = self._load_played_cards()
            player_won = self.check_points()
            if player_won is not None:
                print("Player", player_won.get_id(), "won!")
                self.winner = player_won

                self.set_state(State.ENDED)
            else:
                if self._verbose in (Verboser.INFO, Verboser.DEBUG):
                    print("End of the round.")
                    self._print_player_scores()

                if self._verbose == Verboser.DEBUG:
                    print("Round reset...")

                self._reset_round(player_won_round)
        else:
            # Getting cards that entered in a merged frames
            card = self._get_entering_card(detected_cards)

            if card is None:
                # No new card detected
                return

            if self._verbose in (Verboser.INFO, Verboser.DEBUG):
                print("New card:", card)

            self._cards_in_round.append(Card(card))

    def game_frame(self, detected_cards) -> Union[None, Player]:
        if self.get_state() == State.DEALING:
            self._dealing_stage(detected_cards)

        elif self.get_state() == State.BIDDING:
            self._bidding_stage()

        elif self.get_state() == State.PLAYING:
            self._playing_stage(detected_cards)

        elif self.get_state() == State.ENDED:
            if self._verbose == Verboser.DEBUG:
                print("Game ending...")

            return self.winner
