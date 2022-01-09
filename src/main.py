from pathlib import Path
from argparse import ArgumentParser

from controller import Controller


def create_parser() -> ArgumentParser:
    parser = ArgumentParser(
        description="A tool to detect events in a game of russian schnapsen."
    )

    parser.add_argument(
        "-s",
        "--source",
        type=str,
        required=True,
        help="The source video file to read from.",
    )
    parser.add_argument(
        "-w", "--weights", required=True, help="Path to yolo pre-trained weights",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        choices=["silent", "info", "debug"],
        help="Prints debug information.",
        default="info",
    )

    return parser


if __name__ == "__main__":
    parser = create_parser()
    args = parser.parse_args()

    source_path = Path(args.source).resolve()
    if not source_path.exists():
        raise FileNotFoundError("Source path invalid, file not found")

    weights_path = Path(args.weights).resolve()
    if not weights_path.exists():
        raise FileNotFoundError("Weigths path invalid, file not found")

    controller = Controller(source_path, weights_path, args.verbose)
    controller.run()
