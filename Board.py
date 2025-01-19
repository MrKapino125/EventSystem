import random
import pygame
import Enemy
import Card


class Board:
    def __init__(self, hogwarts_cards, dark_arts_cards, enemies, places, players, screen_size):
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

        self.overlay_width = screen_size[0] // 4
        self.overlay_height = screen_size[1]
        self.overlay_rect = pygame.Rect(-self.overlay_width, 0, self.overlay_width, self.overlay_height)  # start offscreen
        self.overlay_target_x = 0
        self.overlay_speed = 80  # Pixels per frame
        self.text_visible = False
        self.text_delay_counter = 0
        self.text_delay = 1  # frames
        self.current_card = None
        self.font = pygame.font.Font(None, 36)
        self.is_hovering = False

    def tick(self, game_state):
        event_handler = game_state.event_handler

        if event_handler.is_clicked["left"] and not event_handler.is_clicked_lock["left"]:
            for card in game_state.current_player.hand:
                if card.is_hovering(event_handler.mouse_pos):
                    game_state.current_player.play_card(card, game_state)
                    game_state.card_position_manager.align_hands()
                    break

        for card in self.shop_cards + [card for player in self.players for card in player.hand] + self.open_enemies:
            is_hovering = card.is_hovering(event_handler.mouse_pos)

            if is_hovering:
                self.current_card = card
                self.is_hovering = True
                break
        else:
            self.is_hovering = False

        if self.is_hovering and self.overlay_rect.x < self.overlay_target_x:
            self.overlay_rect.x += self.overlay_speed
            if self.overlay_rect.x >= self.overlay_target_x:
                self.overlay_rect.x = self.overlay_target_x
                self.text_visible = True

        elif not self.is_hovering and self.overlay_rect.x > -self.overlay_width:
            self.overlay_rect.x -= self.overlay_speed
            if self.overlay_rect.x <= -self.overlay_width:
                self.overlay_rect.x = -self.overlay_width
                self.text_visible = False

    def render(self, screen):
        pygame.draw.rect(screen, (181, 101, 29), (self.pos[0], self.pos[1], self.width, self.height))

        for shop_card in self.shop_cards:
            shop_card.render(screen)
        for enemy in self.open_enemies:
            enemy.render(screen)
        hand_cards = [card for player in self.players for card in player.hand]
        for card in hand_cards:
            card.render(screen)

        self.render_overlay(screen)

    def render_overlay(self, screen):
        s = pygame.Surface((self.overlay_rect.width, self.overlay_rect.height), pygame.SRCALPHA)  # per-pixel alpha
        s.fill((128, 128, 128, 128))  # values 0-255
        screen.blit(s, (self.overlay_rect.x, self.overlay_rect.y))

        if self.text_visible:
            reward_text = None
            if isinstance(self.current_card, Card.HogwartsCard):
                card_name = self.current_card.data["name"]
                card_description = self.current_card.data["description"]
            elif isinstance(self.current_card, Enemy.Enemy):
                card_name = self.current_card.name
                card_description = self.current_card.description
                reward_text = self.current_card.reward_text
            else:
                card_name = ""
                card_description = ""

            name_text = self.font.render(card_name, True, (0, 0, 0))
            name_rect = name_text.get_rect(center=(self.overlay_rect.centerx, self.overlay_rect.centery - 40))  # moved name up

            screen.blit(name_text, name_rect)

            effect_rect = pygame.Rect(self.overlay_rect.x + 10, self.overlay_rect.centery - 20, self.overlay_rect.width - 20, 100)
            reward_rect = pygame.Rect(self.overlay_rect.x + 10, self.overlay_rect.centery - 20 + effect_rect.height + 20, self.overlay_rect.width - 20, 100)

            self.draw_multiline_text(screen, card_description, self.font, (0, 0, 0), effect_rect)  # added small padding
            if reward_text is not None:
                self.draw_multiline_text(screen, reward_text, self.font, (0, 0, 0), reward_rect)  # added small padding

    def draw_multiline_text(self, surface, text, font, color, rect):
        words = text.split()
        lines = []
        current_line = []
        for word in words:
            test_line = " ".join(current_line + [word])
            test_rect = font.render(test_line, True, color).get_rect()
            if test_rect.width <= rect.width:
                current_line.append(word)
            else:
                lines.append(" ".join(current_line))
                current_line = [word]
        lines.append(" ".join(current_line))  # Add the last line

        y_offset = 0
        for line in lines:
            text_surface = font.render(line, True, color)
            text_rect = text_surface.get_rect(center=(rect.centerx, rect.centery + y_offset))
            surface.blit(text_surface, text_rect)
            y_offset += text_rect.height  # Move down for the next line

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
            player.shuffle_deck()
            player.draw_5()

    def play_dark_arts(self):
        if not self.dark_arts_stack:
            self.reshuffle_dark_arts()

        dark_arts_card = self.dark_arts_stack.pop()
        dark_arts_card.play()
        self.dark_arts_stack.append(dark_arts_card)

    def reshuffle_dark_arts(self):
        if self.dark_arts_stack:
            raise Exception("Dark Arts Deck not empty, no shuffle needed!")

        self.dark_arts_stack = self.dark_arts_dump[:]  # Create a copy to avoid modifying the original discard pile
        self.dark_arts_dump = []
        random.shuffle(self.dark_arts_stack)
