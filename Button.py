import pygame
import re

from Effect import Effect


class Button:
    def __init__(self, text="", color=(255, 0, 0), back_color=(255, 255, 255)):
        self.pos = (0, 0)
        self.width = 0
        self.height = 0
        self.font_size = 20
        self.font = pygame.font.SysFont("Arial", self.font_size)
        self.text = text
        self.selected = False
        self.color = color
        self.back_color = back_color

        self.lines = []

    def render(self, screen, pos=None, width=None, height=None):
        altered = True
        if pos is None:
            pos = self.pos
            altered = False
        if width is None:
            width = self.width
            altered = False
        if height is None:
            height = self.height
            altered = False


        fill_surface = pygame.Surface((width, height), pygame.SRCALPHA)
        pygame.draw.rect(fill_surface, (*self.back_color, 128), (0, 0, width, height))

        screen.blit(fill_surface, (pos[0], pos[1]))

        pygame.draw.rect(screen, self.color, (pos[0], pos[1], width, height), 2)

        if altered:
            lines = self.generate_lines(pos, width, height)
        else:
            lines = self.lines

        y_offset = 0
        line_spacing = 5  # spacing between lines
        for line in lines:
            text_surface = self.font.render(line, True, self.color)
            text_rect = text_surface.get_rect(center=(pos[0] + width // 2,
                                                      pos[1] + height // 2 + y_offset - (len(lines) - 1) * (
                                                                  self.font_size + line_spacing) // 2))  # vertical align
            screen.blit(text_surface, text_rect)
            y_offset += self.font_size + line_spacing

        if self.selected:
            self.render_selected(screen, pos=pos, width=width, height=height)

    def render_selected(self, screen, pos=None, width=None, height=None, color=(0, 255, 0)):
        if pos is None:
            pos = self.pos
        if width is None:
            width = self.width
        if height is None:
            height = self.height

        thickness = 4  # Outline thickness

        # Create a rectangle for the outline
        outline_rect = pygame.Rect(pos[0] - thickness, pos[1] - thickness,
                                   width + 2 * thickness, height + 2 * thickness)

        pygame.draw.rect(screen, color, outline_rect, thickness)

    def render_select_overlay(self, screen, pos=None, width=None, height=None):
        self.render(screen, pos, width, height)

    def generate_lines(self, pos=None, width=None, height=None):
        if pos is None:
            pos = self.pos
        if width is None:
            width = self.width
        if height is None:
            height = self.height

        text = self.text

        font = self.font
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

        return get_lines(words)

    def is_hovering(self, mouse_pos):
        mouse_x, mouse_y = mouse_pos
        rect_x, rect_y = self.pos
        rect_width, rect_height = self.width, self.height

        if (rect_x <= mouse_x <= rect_x + rect_width and
                rect_y <= mouse_y <= rect_y + rect_height):
            return True
        else:
            return False


class EffectButton(Button):
    def __init__(self, effect, game_state):
        super().__init__()
        self.effect = effect
        self.can_use = True
        self.game_state = game_state

    def render(self, screen, pos=None, width=None, height=None):
        super().render(screen, pos, width, height)
        if pos is None:
            pos = self.pos
        if width is None:
            width = self.width
        if height is None:
            height = self.height

        effect = self.game_state.get_effect_from_type(self.effect["type"], self.effect)
        if not isinstance(effect, Effect):
            return
        if not self.game_state.can_use_effect(effect):
            self.render_x(screen, pos, width, height)

    def render_x(self, screen, pos, width, height):
        gray = (128, 128, 128)  # Graue Farbe
        overlay = pygame.Surface((width, height), pygame.SRCALPHA)  # Transparente Oberfläche
        overlay.fill((*gray, 128))  # Füllfarbe mit Alpha-Wert für Transparenz (128 von 255)
        screen.blit(overlay, pos)

    def set_text(self):
        self.text = self.generate_effect_text()
        if self.text is None:
            self.text = f"{self.effect['type']} {self.effect.get('amount')} {self.effect.get('target')}"

        self.lines = self.generate_lines()

    def generate_effect_text(self):
        if self.effect["type"] == "damage":
            if self.effect["amount"] == 1:
                heart = "Herz"
            else:
                heart = "Herzen"
            if self.effect["target"] == "self":
                return f"Du verlierst {self.effect['amount']} {heart}!"
            elif self.effect["target"] == "choice":
                return f"Ein Held deiner Wahl verliert {self.effect['amount']} {heart}!"
            elif self.effect["target"] == "all":
                return f"ALLE Helden verlieren {self.effect['amount']} {heart}!"

        elif self.effect["type"] == "heal":
            if self.effect["amount"] == 1:
                heart = "Herz"
            else:
                heart = "Herzen"
            if self.effect["target"] == "self":
                return f"Du erhältst {self.effect['amount']} {heart}!"
            elif self.effect["target"] == "choice":
                return f"Ein Held deiner Wahl erhält {self.effect['amount']} {heart}!"
            elif self.effect["target"] == "all":
                return f"ALLE Helden erhalten {self.effect['amount']} {heart}!"

        elif self.effect["type"] == "give_coins":
            if self.effect["amount"] == 1:
                coin = "Münze"
            else:
                coin = "Münzen"
            if self.effect["target"] == "self":
                return f"Du erhältst {self.effect['amount']} {coin}!"
            elif self.effect["target"] == "choice":
                return f"Ein Held deiner Wahl erhält {self.effect['amount']} {coin}!"
            elif self.effect["target"] == "all":
                return f"ALLE Helden erhalten {self.effect['amount']} {coin}!"

        elif self.effect["type"] == "give_bolts":
            if self.effect["amount"] == 1:
                bolt = "Blitz"
            else:
                bolt = "Blitze"
            if self.effect["target"] == "self":
                return f"Du erhältst {self.effect['amount']} {bolt}!"
            elif self.effect["target"] == "choice":
                return f"Ein Held deiner Wahl erhält {self.effect['amount']} {bolt}!"
            elif self.effect["target"] == "all":
                return f"ALLE Helden erhalten {self.effect['amount']} {bolt}!"

        elif self.effect["type"] == "drop_cards":
            translation = {"spell": {1: "Spruch", 2: "Sprüche"},
                           "ally": {1: "Verbündeten", 2: "Verbündete"},
                           "object": {1: "Gegenstand", 2: "Gegenstände"},
                           None: {1: "Karte", 2: "Karten"}}
            amount = 2 if self.effect["amount"] != 1 else 1
            card = translation[self.effect.get("card_type")][amount]

            if self.effect["target"] == "self":
                return f"Wirf {self.effect['amount']} {card} ab!"

        elif self.effect["type"] == "draw_cards":
            if self.effect["amount"] == 1:
                card = "Karte"
            else:
                card = "Karten"

            if self.effect["target"] == "self":
                return f"Ziehe {self.effect['amount']} {card}!"

        elif self.effect["type"][:6] == "redraw":
            card_type = self.effect["type"].split("_")[1]
            translation = {"spell": "Spruch",
                           "ally": "Verbündeten",
                           "object": "Gegenstand"}
            return f"Nimm einen {translation[card_type]} von deinem Ablagestapel!"

        elif self.effect["type"] == "remove_skulls":
            if self.effect["amount"] == 1:
                card = "Totenkopf"
            else:
                card = "Totenköpfe"
            return f"Entferne {self.effect['amount']} {card}"

    def parse_effect_type(self, effect_type):
        pass


class CardButton(Button):
    def __init__(self, card):
        super().__init__()
        self.card = card

    def render(self, screen, pos=None, width=None, height=None):
        super().render(screen, pos, width, height)

    def set_text(self):
        self.text = f"{self.card.get_name()}"
        self.lines = self.generate_lines()

    def render_x(self, screen, pos=None, width=None, height=None):
        if pos is None:
            pos = self.pos
        if width is None:
            width = self.width
        if height is None:
            height = self.height

        gray = (128, 128, 128)  # Graue Farbe
        overlay = pygame.Surface((width, height), pygame.SRCALPHA)  # Transparente Oberfläche
        overlay.fill((*gray, 128))  # Füllfarbe mit Alpha-Wert für Transparenz (128 von 255)
        screen.blit(overlay, pos)
