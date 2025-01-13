import random


class Board:
    def __init__(self, hogwarts_cards, dark_arts_cards, enemies, places):
        self.open_enemies = []
        self.enemy_stack = enemies
        self.enemy_dump = []
        self.places = places
        self.active_place = None
        self.hogwarts_stack = hogwarts_cards
        self.shop_cards = []
        self.dark_arts_stack = dark_arts_cards
        self.dark_arts_dump = []

    def render(self, screen):
        for shop_card in self.shop_cards:
            shop_card.render(screen)

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

    def reshuffle_dark_arts(self):
        if self.dark_arts_stack:
            raise Exception("Dark Arts Deck not empty, no shuffle needed!")

        self.dark_arts_stack = self.dark_arts_dump[:]  # Create a copy to avoid modifying the original discard pile
        self.dark_arts_dump = []
        random.shuffle(self.dark_arts_stack)
