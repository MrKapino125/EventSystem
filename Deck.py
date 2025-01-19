import pygame


class Deck(list):
    def __init__(self):
        super().__init__()
        self.pos = (0, 0)
        self.width = 0
        self.height = 0

    def render(self, screen):
        fill_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        pygame.draw.rect(fill_surface, (255, 255, 255, 128), (0, 0, self.width, self.height))

        screen.blit(fill_surface, (self.pos[0], self.pos[1]))

        pygame.draw.rect(screen, (255, 0, 0), (self.pos[0], self.pos[1], self.width, self.height), 2)

        font_size = 20
        font = pygame.font.Font(None, font_size)
        text_surface = font.render(str(len(self)), True, (255, 0, 0))
        text_rect = text_surface.get_rect(center=(self.pos[0] + self.width // 2,
                                                  self.pos[1] + self.height // 2))
        screen.blit(text_surface, text_rect)

    def is_hovering(self, mouse_pos):
        mouse_x, mouse_y = mouse_pos
        rect_x, rect_y = self.pos
        rect_width, rect_height = self.width, self.height

        if (rect_x <= mouse_x <= rect_x + rect_width and
                rect_y <= mouse_y <= rect_y + rect_height):
            return True
        else:
            return False


class DiscardPile(Deck):
    def __init__(self):
        super().__init__()

    def render(self, screen):
        if len(self) == 0:
            return

        self[len(self) - 1].render(screen, self.pos, self.width, self.height)
