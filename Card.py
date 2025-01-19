import json
import Effect
import pygame
import re


class Card:
    def __init__(self, data):
        self.data = data
        self.pos = (0, 0)
        self.width = 0
        self.height = 0

    def __repr__(self):
        return self.data["name"]

    def play(self, source, game_state):
        pass

    def is_hovering(self, mouse_pos):
        mouse_x, mouse_y = mouse_pos
        rect_x, rect_y = self.pos
        rect_width, rect_height = self.width, self.height

        if (rect_x <= mouse_x <= rect_x + rect_width and
                rect_y <= mouse_y <= rect_y + rect_height):
            return True
        else:
            return False

    def render(self, screen, pos=None, width=None, height=None):
        if pos is None:
            pos = self.pos
        if width is None:
            width = self.width
        if height is None:
            height = self.height

        fill_surface = pygame.Surface((width, height), pygame.SRCALPHA)
        pygame.draw.rect(fill_surface, (255, 255, 255, 128), (0, 0, width, height))

        screen.blit(fill_surface, (pos[0], pos[1]))

        pygame.draw.rect(screen, (255, 0, 0), (pos[0], pos[1], width, height), 2)

        text = self.data["name"]

        font_size = 20
        font = pygame.font.Font(None, font_size)
        words = re.split(r"([ -])", text)
        lines = []
        current_line = ""

        for word in words:
            if word == "-":
                test_line = current_line[:-1] + word + " "
            else:
                test_line = current_line + word + " "
            text_width, _ = font.size(test_line)
            if text_width <= width - 10:  # Add a small padding
                current_line = test_line
            else:
                lines.append(current_line)
                current_line = word + " "
        lines.append(current_line)  # Add the last line

        y_offset = 0
        line_spacing = 5  # spacing between lines
        for line in lines:
            text_surface = font.render(line, True, (255,0,0))
            text_rect = text_surface.get_rect(center=(pos[0] + width // 2, pos[1] + height // 2 + y_offset - (len(lines) - 1) * (font_size + line_spacing) // 2))  # vertical align
            screen.blit(text_surface, text_rect)
            y_offset += font_size + line_spacing


class HogwartsCard(Card):
    def __init__(self, data):
        super().__init__(data)

    def play(self, source, game_state):
        game_state.apply_effect(Effect.CardPlayEffect(self), source, [game_state.current_player])


class DarkArtsCard(Card):
    def __init__(self, data):
        super().__init__(data)

    def play(self, source, game_state):
        game_state.apply_effect(Effect.CardPlayEffect(self), self, [game_state.current_player])


class PlaceCard(Card):
    def __init__(self, data):
        super().__init__(data)
        self.skulls = 0
        self.max_skulls = self.data["max_skulls"]

    def add_skulls(self, skulls):
        self.skulls += skulls
        if self.skulls > self.max_skulls:
            self.skulls = self.max_skulls

    def remove_skulls(self, skulls):
        self.skulls -= skulls
        if self.skulls < 0:
            self.skulls = 0


def load_cards(level):
    hogwarts_cards = load_hogwarts_cards(level)
    place_cards = load_place_cards(level)
    dark_arts_cards = load_dark_arts_cards(level)
    
    return hogwarts_cards, place_cards, dark_arts_cards


def load_hogwarts_cards(level):
    with open("card_data/hogwarts_card_data.json", "r", encoding="UTF-8") as f:
        cards = []
        cards_dict = json.load(f)
        for card in cards_dict:
            if card["level"] <= level:
                amount = card.get("amount", 1)
                for i in range(amount):
                    cards.append(HogwartsCard(card))

        return cards


def load_place_cards(level):
    with open("card_data/place_card_data.json", "r", encoding="UTF-8") as f:
        cards = []
        cards_dict = json.load(f)
        for card in cards_dict:
            if card["level"] == level:
                cards.append(PlaceCard(card))

        return cards


def load_dark_arts_cards(level):
    with open("card_data/dark_arts_card_data.json", "r", encoding="UTF-8") as f:
        cards = []
        cards_dict = json.load(f)
        for card in cards_dict:
            if card["level"] <= level:
                cards.append(DarkArtsCard(card))

        return cards

