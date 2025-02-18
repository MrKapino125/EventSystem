import pygame
import re


class Button:
    def __init__(self, text=""):
        self.pos = (0, 0)
        self.width = 0
        self.height = 0
        self.font_size = 20
        self.font = pygame.font.SysFont("Arial", self.font_size)
        self.text = text
        self.selected = False

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
        pygame.draw.rect(fill_surface, (255, 255, 255, 128), (0, 0, width, height))

        screen.blit(fill_surface, (pos[0], pos[1]))

        pygame.draw.rect(screen, (255, 0, 0), (pos[0], pos[1], width, height), 2)

        if altered:
            lines = self.generate_lines(pos, width, height)
        else:
            lines = self.lines

        y_offset = 0
        line_spacing = 5  # spacing between lines
        for line in lines:
            text_surface = self.font.render(line, True, (255, 0, 0))
            text_rect = text_surface.get_rect(center=(pos[0] + width // 2,
                                                      pos[1] + height // 2 + y_offset - (len(lines) - 1) * (
                                                                  self.font_size + line_spacing) // 2))  # vertical align
            screen.blit(text_surface, text_rect)
            y_offset += self.font_size + line_spacing

        if self.selected:
            green = (0, 255, 0)  # Green color
            thickness = 4  # Outline thickness

            # Create a rectangle for the outline
            outline_rect = pygame.Rect(self.pos[0] - thickness, self.pos[1] - thickness,
                                       self.width + 2 * thickness, self.height + 2 * thickness)

            pygame.draw.rect(screen, green, outline_rect, thickness)

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

        words = re.split(r"([ -])", text)
        words = [word for word in words if word != " "]

        return words

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
    def __init__(self, effect):
        super().__init__()
        self.effect = effect
        self.can_use = True

    def set_text(self):
        self.text = f"{self.effect['type']} {self.effect.get('amount')} {self.effect.get('target')}"
        self.lines = self.generate_lines()

    def parse_effect_type(self, effect_type):
        pass


class CardButton(Button):
    def __init__(self, card):
        super().__init__()
        self.card = card

    def set_text(self):
        self.text = f"{self.card.data['name']}"
        self.lines = self.generate_lines()
