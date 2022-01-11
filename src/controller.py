import sys
from pathlib import Path

import cv2
import numpy as np
import pandas as pd

from detector import Detector
from game import Game
from player import Player
from state import State
from verboser import Verboser

MERGE_FRAMES = 10


class Controller:
    def __init__(
        self, source_path: Path, weights_path: Path, verbose: str, no_show: bool
    ) -> None:
        self._source_path = source_path
        self._verbose: Verboser = Verboser(verbose)
        self._no_show = no_show

        self.detector = Detector(weights_path)
        self.game = Game(verbose)

    def run(self):
        font = cv2.FONT_HERSHEY_PLAIN
        cap = cv2.VideoCapture(str(self._source_path))
        if not cap.isOpened():
            raise RuntimeError("Could not open video")

        frame_counter = 0
        detector_buffer = None
        while cap.isOpened():
            ret, frame = cap.read()
            frame_counter += 1

            if not ret:
                break

            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            detected_cards = self.detector.detect_cards(frame)

            if detector_buffer is None:
                detector_buffer = detected_cards
            else:
                detector_buffer = detector_buffer.append(
                    detected_cards, ignore_index=True
                )

            if not self._no_show:
                # Add labels to detection
                for det_card in detected_cards.itertuples():
                    xmin, ymin, xmax, ymax = (
                        int(det_card.xmin),
                        int(det_card.ymin),
                        int(det_card.xmax),
                        int(det_card.ymax),
                    )

                    cv2.rectangle(
                        frame, (xmin, ymin), (xmax, ymax), (0, 128, 0), 2,
                    )
                    cv2.putText(
                        frame,
                        det_card.name,
                        (xmin, ymin - 10),
                        font,
                        2,
                        (0, 128, 0),
                        2,
                    )

                cv2.imshow("frame", cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))
                if cv2.waitKey(25) & 0xFF == ord("q"):
                    break

            if frame_counter % MERGE_FRAMES == 0:
                try:
                    winner = self.game.game_frame(detector_buffer)
                except Exception as e:
                    print(e)
                    print("Terminating due to error")
                    sys.exit(-1)

                if winner is not None:
                    break
                else:
                    frame_counter = 0
                    detector_buffer = None

        cap.release()
        cv2.destroyAllWindows()
        # TODO: Get points from game
        if winner is not None:
            self.print_winner(winner)
        else:
            print("Winner has not been determined")

    def print_winner(self, winner):
        print(f"Player {winner.get_id()} won the game of Russian Schnapsen!")


if __name__ == "__main__":
    c = Controller()
    c.run()
