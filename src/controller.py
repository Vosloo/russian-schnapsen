from pathlib import Path

import cv2

from detector import Detector
from game import Game
from player import Player
from state import State


class Controller:
    def __init__(
        self,
        source_path: Path,
        weights_path: Path,
        verbose: bool = False,
    ) -> None:
        self._source_path = source_path
        self._verbose: bool = verbose

        self.detector = Detector(source_path, weights_path)
        self.game = Game()

    def run(self):
        cap = cv2.VideoCapture(str(self._source_path))
        if not cap.isOpened():
            raise RuntimeError("Could not open video")

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            detected_cards = self.detector.detect_cards(frame)
            if self._verbose:
                print(detected_cards)

            self.game.game_frame(detected_cards)

    def print_winner(self, winner):
        print(f"Player {winner.get_id()} won the game of Russian Schnapsen!")


if __name__ == "__main__":
    c = Controller()
    c.run()