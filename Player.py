import random
import Effect
import Event
from State import GameState
import Deck
import pygame
import math


class Player:
    def __init__(self, name):
        self.name = name
        self.names = self.name.split(" ")
        self.health = 10

        self.coins = 0
        self.bolts = 0
        self.deck = Deck.Deck()
        self.hand = []
        self.discard_pile = Deck.DiscardPile()
        self.is_dead = False

        self.pos = (0, 0)
        self.width = 0
        self.height = 0
        self.circle_radius = 0
        self.character_circle_center = (0, 0)
        self.health_circle_center = (0, 0)
        self.coins_circle_center = (0, 0)
        self.bolts_circle_center = (0, 0)

    def render(self, screen):
        self.render_hand(screen)

        self.render_deck(screen)
        self.render_discard_pile(screen)
        self.render_stats(screen)

    def render_select_overlay(self, screen):
        green = (0, 255, 0)  # Green color
        thickness = 4  # Outline thickness

        pygame.draw.circle(screen, green, self.character_circle_center, self.circle_radius, thickness)

    def is_hovering(self, mouse_pos):
        distance = math.sqrt((mouse_pos[0] - self.character_circle_center[0]) ** 2 + (mouse_pos[1] - self.character_circle_center[1]) ** 2)
        return distance <= self.circle_radius

    def render_hand(self, screen):
        for card in self.hand:
            card.render(screen)

    def render_deck(self, screen):
        self.deck.render(screen)

    def render_discard_pile(self, screen):
        self.discard_pile.render(screen)

    def render_stats(self, screen):
        self.render_circles(screen, self.pos, self.names[0][0] + self.names[1][0], self.health, True)
        self.render_circles(screen, (self.pos[0] + 7 * self.width / 8, self.pos[1]), self.coins, self.bolts, False)

    def render_circles(self, screen, pos, num1, num2, is_left):
        width, height = self.width / 8, self.height
        x, y = pos[0], pos[1]

        # Calculate padding
        padding = width / 32

        # Calculate available width for circles
        available_width = width - 3 * padding  # 3 paddings: left, between circles, right

        # Calculate circle diameter (and radius)
        circle_diameter = min(available_width / 2, height - 2 * padding)
        circle_radius = circle_diameter / 2

        # Calculate circle centers
        left_circle_center = (x + padding + circle_radius, y + padding + circle_radius)
        right_circle_center = (x + 2 * padding + 3 * circle_radius, y + padding + circle_radius)

        self.circle_radius = circle_radius
        if is_left:
            self.character_circle_center = left_circle_center
            self.health_circle_center = right_circle_center
        else:
            self.coins_circle_center = left_circle_center
            self.bolts_circle_center = right_circle_center

        # Draw the circles
        pygame.draw.circle(screen, (255, 0, 0), left_circle_center, circle_radius, 2)
        pygame.draw.circle(screen, (255, 0, 0), right_circle_center, circle_radius, 2)

        font = pygame.font.Font(None, int(circle_radius))

        self.render_centered_text(screen, str(num1), font, (0, 0, 0), left_circle_center)
        self.render_centered_text(screen, str(num2), font, (0, 0, 0), right_circle_center)

    def render_centered_text(self, screen, text, font, color, center):
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect(center=center)
        screen.blit(text_surface, text_rect)

    def apply_hero_effect(self, event, game_state):
        pass

    def play_card(self, card, game_state):
        if card in self.hand:
            self.hand.remove(card)
            self.discard_pile.append(card)
            card.play(self, game_state)

    def drop_card(self, card, game_state):
        if card in self.hand:
            self.hand.remove(card)
            self.discard_pile.append(card)

    def buy_card(self, card, game_state):
        cost = card.data["cost"]
        if self.coins >= cost:
            game_state.event_handler.dispatch_event(Event.BuyCardEvent(self, card))

    def damage_enemy(self, enemy, game_state):
        if self.bolts > 0:
            game_state.apply_effect(Effect.DamageEffect(1), self, [enemy])

    def apply_end_turn_effect(self, game_state):
        self.coins = 0
        self.bolts = 0

        while len(self.hand) > 0:
            self.discard_pile.append(self.hand.pop())
        self.draw_5()

    def apply_heal_effect(self, amount, game_state):
        self.heal(amount)

    def apply_damage_effect(self, amount, game_state, event):
        if self.is_dead:
            return
        self.take_damage(amount)
        if self.is_dead:
            game_state.event_handler.dispatch_event(Event.PlayerDeadEvent(event.data.get("source"), self))

    def apply_give_bolts_effect(self, amount, game_state):
        self.give_bolts(amount)

    def apply_give_coins_effect(self, amount, game_state):
        self.give_coins(amount)

    def apply_draw_card_effect(self, amount, game_state):
        for _ in range(amount):
            self.draw_card()

    def apply_drop_card_effect(self, event, game_state):
        card = event.data["card"]
        self.drop_card(card, game_state)

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
        if self.is_dead:
            return

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
            self.health = 0
            self.is_dead = True

    def die(self, game_state, source):
        self.coins = 0
        self.bolts = 0

        game_state.select_drop_cards([self], None, len(self.hand) // 2, source)

    def shuffle_deck(self):
        random.shuffle(self.deck)

    def reshuffle_deck(self):
        if self.deck:
            raise Exception("Deck not empty, no shuffle needed!")
        if self.discard_pile:
            self.deck.extend(self.discard_pile)  # Add all elements from the discard pile to the deck
            self.discard_pile.clear()  # Clear the discard pile
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
        super().apply_end_turn_effect(game_state)
        self.effect_played = False
