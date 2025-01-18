import random
import Effect
from State import GameState


class Player:
    def __init__(self, name):
        self.name = name
        self.health = 10
        self.coins = 0
        self.bolts = 0
        self.deck = []
        self.hand = []
        self.discard_pile = []

        self.pos = (0,0)
        self.width = 0
        self.height = 0

    def render(self, screen):
        # TODO render  deck, pile, hearts, coins, bolts
        self.render_hand(screen)

    def render_hand(self, screen):
        for card in self.hand:
            card.render(screen)

    def apply_hero_effect(self, event, game_state):
        pass

    def play_card(self, card, game_state):
        if card in self.hand:
            self.hand.remove(card)
            self.discard_pile.append(card)
            card.play(self, game_state)

    def apply_end_turn_effect(self, game_state):
        self.coins = 0
        self.bolts = 0

        self.draw_5()

    def apply_heal_effect(self, amount, game_state):
        self.heal(amount)

    def apply_damage_effect(self, amount, game_state):
        self.take_damage(amount)

    def apply_give_bolts_effect(self, amount, game_state):
        self.give_bolts(amount)

    def apply_give_coins_effect(self, amount, game_state):
        self.give_coins(amount)

    def apply_draw_card_effect(self, amount, game_state):
        for _ in range(amount):
            self.draw_card()

    def draw_5(self):
        for _ in range(5):
            self.draw_card()

    def draw_card(self):
        if not self.deck:
            self.reshuffle_deck()

        card = self.deck.pop()
        self.hand.append(card)

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

    def shuffle_deck(self):
        random.shuffle(self.deck)

    def reshuffle_deck(self):
        if self.deck:
            raise Exception("Deck not empty, no shuffle needed!")
        if self.discard_pile:
            self.deck = self.discard_pile[:]  # Create a copy to avoid modifying the original discard pile
            self.discard_pile = []
            random.shuffle(self.deck)


class Harry(Player):
    def __init__(self):
        super().__init__("Harry Potter")
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

    def apply_end_turn_effect(self, game_state):
        super().apply_end_turn_effect(game_state)
        self.effect_played = False


class Neville(Player):
    def __init__(self):
        super().__init__("Neville Longbottom")
        self.first_heal_given_this_turn = {}
        self.effect_played = False

    def apply_hero_effect(self, event, game_state):
        target = event.data['target']

        if target.health == 0 or target.health == 10:
            return

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

    def apply_end_turn_effect(self, game_state):
        super().apply_end_turn_effect(game_state)
        self.first_heal_given_this_turn = {}


class Ron(Player):
    def __init__(self):
        super().__init__("Ron Weasley")
        self.enemies_attacked = {}
        self.effect_played = False

    def apply_hero_effect(self, event, game_state: GameState):
        if self.effect_played:
            return

        target = event.data['target']
        amount = event.data['amount']

        if target not in self.enemies_attacked:
            self.enemies_attacked[target] = amount
        else:
            self.enemies_attacked[target] += amount

        if target.health == 0 or target.health == 10:
            return

        if self.enemies_attacked[target] >= 3:
            self.effect_played = True
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

    def apply_end_turn_effect(self, game_state):
        super().apply_end_turn_effect(game_state)
        self.enemies_attacked = {}
        self.effect_played = False


class Hermione(Player):
    def __init__(self):
        super().__init__("Hermine Granger")
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

    def apply_end_turn_effect(self, game_state):
        self.effect_played = False
