import json
import Effect
from State import GameState


class Card(object):
    def __init__(self, data):
        self.data = data

    def play(self, source, game_state: GameState):
        game_state.apply_effect(Effect.CardPlayEffect(self.data), source, [self])


def load_cards(level):
    with open("card_data.json", "r", encoding="UTF-8") as f:
        cards = []
        cards_dict = json.load(f)
        for card in cards_dict:
            if card["level"] <= level:
                cards.append(Card(card))

        return cards
