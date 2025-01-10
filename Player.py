import random
import Effect
from State import GameState


class Player:
    def __init__(self, name, deck):
        self.name = name
        self.health = 10
        self.coins = 0
        self.bolts = 0
        self.deck = deck
        self.hand = []
        self.discard_pile = []

    def apply_hero_effect(self, event, game_state):
        pass

    def handle_end_turn(self, game_state):
        self.coins = 0
        self.bolts = 0

    def apply_heal_effect(self, amount, game_state):
        self.heal(amount)

    def apply_damage_effect(self, amount, game_state):
        self.take_damage(amount)

    def apply_give_bolts_effect(self, amount, game_state):
        self.give_bolts(amount)

    def apply_give_coins_effect(self, amount, game_state):
        self.give_coins(amount)

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

    def give_bolts(self, amount):
        self.bolts += amount

    def give_coins(self, amount):
        self.coins += amount

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
        self.effect_played = False

    def apply_hero_effect(self, event, game_state):
        if self.effect_played:
            return

        self.effect_played = True
        effect = Effect.GiveBoltEffect(1)
        if 3 <= game_state.level <= 6:
            available_targets = game_state.get_available_targets_for_effect(effect, self)
            if available_targets:
                target = game_state.select_single_target(self, available_targets)
                game_state.apply_effect(effect, self, [target])
            else:
                print("No available targets")
        if game_state.level == 7:
            available_targets = game_state.get_available_targets_for_effect(effect, self)
            if available_targets:
                targets = game_state.select_multiple_targets(self, 2, available_targets)
                game_state.apply_effect(Effect.GiveBoltEffect(1), self, targets)
            else:
                print("No available targets")

    def handle_end_turn(self, game_state):
        super().handle_end_turn(game_state)
        self.effect_played = False


class Neville(Player):
    def __init__(self, deck):
        super().__init__("Neville Longbottom", deck)
        self.first_heal_given_this_turn = {}
        self.effect_played = False

    def apply_hero_effect(self, event, game_state):
        target = event.data['target']

        if 3 <= game_state.level <= 6:
            if not self.first_heal_given_this_turn.get(target, False):
                self.first_heal_given_this_turn[target] = True
                game_state.apply_effect(Effect.HealEffect(1), self, [target])
        if game_state.level == 7:
            if not self.effect_played:
                self.effect_played = True
                game_state.apply_effect(Effect.HealEffect(1), self, [target])
            else:
                self.effect_played = False

    def handle_end_turn(self, game_state):
        super().handle_end_turn(game_state)
        self.first_heal_given_this_turn = {}


class Ron(Player):
    def __init__(self, deck):
        super().__init__("Ron Weasley", deck)
        self.enemies_attacked = {}
        self.effect_played = False

    def apply_hero_effect(self, event, game_state: GameState):
        target = event.data['target']
        amount = event.data['amount']

        if self.effect_played:
            return

        if target not in self.enemies_attacked:
            self.enemies_attacked[target] = amount
        else:
            self.enemies_attacked[target] += amount

        if self.enemies_attacked[target] >= 3:
            effect = Effect.HealEffect(2)
            if 3 <= game_state.level <= 6:
                available_targets = game_state.get_available_targets_for_effect(effect, self)
                if available_targets:
                    target = game_state.select_single_target(self, available_targets)

                    game_state.apply_effect(effect, self, [target])
                else:
                    print("No available targets")
            elif game_state.level == 7:
                game_state.apply_effect(effect, self, game_state.players)

            self.effect_played = True

    def handle_end_turn(self, game_state):
        super().handle_end_turn(game_state)
        self.enemies_attacked = {}
        self.effect_played = False


class Hermione(Player):
    def __init__(self, deck):
        super().__init__("Hermione Granger", deck)
        self.spell_played = 0
        self.effect_played = False

    def apply_hero_effect(self, event, game_state):
        if self.effect_played:
            return

        self.spell_played += event.data['amount']
        if self.spell_played >= 4:
            self.effect_played = True

            effect = Effect.GiveCoinsEffect(1)
            if 3 <= game_state.level <= 6:
                available_targets = game_state.get_available_targets_for_effect(effect, self)
                if available_targets:
                    target = game_state.select_single_target(self, available_targets)

                    game_state.apply_effect(effect, self, [target])
                else:
                    print("No available targets")
            elif game_state.level == 7:
                game_state.apply_effect(effect, self, game_state.players)

    def handle_end_turn(self, game_state):
        pass
