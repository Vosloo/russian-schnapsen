import json

CARDS = "cards"
TRUMPS = "trumps"

scores = None
trumps = None

with open("data/card_scores.json") as infile:
    scores = json.load(infile)
    scores, trumps = scores[CARDS], scores[TRUMPS]