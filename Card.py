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

    def drop(self, source, game_state):
        pass

    def select(self, game_state):
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
        words = [word for word in words if word != " "]

        def check_length(word):
            counter = 1
            while counter <= len(word):
                new_word = word[:len(word) - counter]
                text_width, _ = font.size(new_word)
                if text_width <= width - 10:
                    return new_word, word[len(word) - counter:]
                counter += 1
            return "", word  # Return empty string if no suitable split can be found

        def get_lines(words):
            lines = []
            current_line = ""

            i = 0
            while i < len(words):  # Use while loop with index for correct list manipulation
                word = words[i]
                if word == "-":
                    test_line = current_line[:-1] + word + " "
                else:
                    test_line = current_line + word + " "
                text_width, _ = font.size(test_line)

                if text_width <= width - 10:
                    current_line = test_line
                    i += 1  # Increment only if we add the word
                else:
                    word_width, _ = font.size(word)
                    if word_width > width - 10:  # Only split words that are too long on their own
                        new_word, new_word_end = check_length(word)
                        if new_word != "":  # Check if a split was possible
                            words[i] = new_word  # Replace the word with the first part
                            words.insert(i + 1, new_word_end)  # Insert the second part after
                        else:
                            lines.append(current_line)
                            current_line = ""
                            i += 1
                    else:
                        lines.append(current_line)
                        current_line = word + " "
                        i += 1

            lines.append(current_line)
            return lines

        lines = get_lines(words)
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

    def render(self, screen, pos=None, width=None, height=None):
        super().render(screen)

        font = pygame.font.Font(None, 20)

        skulls_surface = font.render(f"{self.skulls} / {self.max_skulls}", True, (255, 0, 0))
        skulls_width = skulls_surface.get_width()
        skulls_height = skulls_surface.get_height()

        # Calculate the center x-coordinate of the box
        center_x = self.pos[0] + self.width // 2

        # Calculate the x-coordinate for centering the health surface
        health_x = center_x - skulls_width // 2

        # Calculate the y-coordinate just above the bottom line of the box
        health_y = self.pos[1] + self.height - skulls_height - self.height // 16

        screen.blit(skulls_surface, (health_x, health_y))

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

        cards.reverse()

        return cards


def load_dark_arts_cards(level):
    with open("card_data/dark_arts_card_data.json", "r", encoding="UTF-8") as f:
        cards = []
        cards_dict = json.load(f)
        for card in cards_dict:
            if card["level"] <= level:
                for _ in range(card.get("amount", 1)):
                    cards.append(DarkArtsCard(card))

        return [card for card in cards if card.data["name"] == "FLIPENDO!"]
        return cards

