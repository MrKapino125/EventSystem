import random
import pygame


class Board:
    def __init__(self, hogwarts_cards, dark_arts_cards, enemies, places, players):
        self.players = players

        self.enemy_stack = enemies
        self.hogwarts_stack = hogwarts_cards
        self.dark_arts_stack = dark_arts_cards
        self.places = places

        self.shop_cards = []
        self.open_enemies = []
        self.hands = {}
        self.active_place = None

        self.enemy_dump = []
        self.dark_arts_dump = []

        self.pos = (0, 0)
        self.width = 0
        self.height = 0

    def tick(self, game_state):
        event_handler = game_state.event_handler

        if event_handler.is_clicked["left"] and not event_handler.is_clicked_lock["left"]:
            for card in self.shop_cards:
                if card.is_hovering(event_handler.mouse_pos):
                    card.play(game_state.current_player, game_state)

    def render(self, screen):
        pygame.draw.rect(screen, (181, 101, 29), (self.pos[0], self.pos[1], self.width, self.height))

        for shop_card in self.shop_cards:
            shop_card.render(screen)
        for enemy in self.open_enemies:
            enemy.render(screen)

    def setup(self, level):
        random.shuffle(self.hogwarts_stack)
        random.shuffle(self.dark_arts_stack)
        random.shuffle(self.enemy_stack)

        if 1 <= level <= 2:
            self.open_enemies.append(self.enemy_stack.pop())
        elif 3 <= level <= 4:
            self.open_enemies.append(self.enemy_stack.pop())
            self.open_enemies.append(self.enemy_stack.pop())
        elif 5 <= level:
            self.open_enemies.append(self.enemy_stack.pop())
            self.open_enemies.append(self.enemy_stack.pop())
            self.open_enemies.append(self.enemy_stack.pop())

        for _ in range(6):
            self.shop_cards.append(self.hogwarts_stack.pop())

        self.active_place = self.places.pop()

        for player in self.players:
            self.hands[player.name] = player.hand


    def reshuffle_dark_arts(self):
        if self.dark_arts_stack:
            raise Exception("Dark Arts Deck not empty, no shuffle needed!")

        self.dark_arts_stack = self.dark_arts_dump[:]  # Create a copy to avoid modifying the original discard pile
        self.dark_arts_dump = []
        random.shuffle(self.dark_arts_stack)
