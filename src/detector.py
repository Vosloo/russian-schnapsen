from pathlib import Path

import pandas as pd
import torch

REPO = "ultralytics/yolov5"
MODEL = "custom"


class Detector:
    def __init__(self, weights_path: Path):
        self._model: Path = weights_path

        # Load the YOLO model
        self.model = torch.hub.load(REPO, MODEL, path=weights_path)

    def detect_cards(self, frame) -> pd.DataFrame:
        """
        Detects the cards in the given frame.

        :param frame: The frame to detect cards in.
        :return: A DataFrame containing the detected cards.
        """
        return self.model(frame).pandas().xyxy[0]

if __name__ == "__main__":
    c = Detector("data/best.pt")
    df = c.detect_cards()