import random
import Effect

class Player:
    def __init__(self, name, deck):
        self.name = name
        self.health = 10
        self.deck = deck
        self.hand = []
        self.discard_pile = []

    def apply_hero_effect(self, event, game_state):
        pass

    def apply_heal_effect(self, amount, game_state):
        self.heal(amount)

    def apply_damage_effect(self, amount, game_state):
        self.take_damage(amount)

    def draw_card(self):
        if self.deck:
            card = self.deck.pop()
            self.hand.append(card)
            return card
        return None  # Handle empty deck

    def discard_card(self, card):
        self.hand.remove(card)
        self.discard_pile.append(card)

    def heal(self, amount):
        self.health += amount
        if self.health > 10:
            self.health = 10

    def take_damage(self, amount):
        self.health -= amount
        if self.health <= 0:
            print(f"{self.name} has been defeated!")

    def reshuffle_deck(self):
        if self.deck:
            raise Exception("Deck not empty, no shuffle needed!")
        if self.discard_pile:
            self.deck = self.discard_pile[:]  # Create a copy to avoid modifying the original discard pile
            self.discard_pile = []
            random.shuffle(self.deck)


class Harry(Player):
    def __init__(self, deck):
        super().__init__("Harry Potter", deck)

    def apply_hero_effect(self, event, game_state):
        pass


class Neville(Player):
    def __init__(self, deck):
        super().__init__("Neville Longbottom", deck)
        self.first_heal_given_this_turn = {}

    def apply_hero_effect(self, event, game_state):
        source = event.data['source']
        target = event.data['target']
        amount = event.data['amount']

        if not self.first_heal_given_this_turn.get(target, False):
            self.first_heal_given_this_turn[target] = True
            game_state.apply_effect(Effect.HealEffect(1), self, [target])

