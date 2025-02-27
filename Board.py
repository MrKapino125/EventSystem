import random
import pygame
import Enemy
import Card
import Deck
import Event
import Player
from Globals import GLOBAL_OVERLAY_FONT_SIZE


class Board:
    def __init__(self, hogwarts_cards, dark_arts_cards, enemies, places, players, game_state):
        self.players = players

        self.enemy_stack = Deck.Deck()
        self.enemy_stack += enemies
        self.hogwarts_stack = hogwarts_cards
        self.dark_arts_stack = Deck.Deck()
        self.dark_arts_stack.extend(dark_arts_cards)
        self.places = places

        self.shop_cards = []
        self.open_enemies = []
        self.hands = {}
        self.active_place = None

        self.enemy_dump = Deck.DiscardPile()
        self.dark_arts_dump = Deck.DiscardPile()
        self.place_dump = Deck.DiscardPile()

        self.pos = (0, 0)
        self.width = 0
        self.height = 0

        screen_size = game_state.screen_size
        self.game_state = game_state
        self.overlay_width = screen_size[0] // 4
        self.overlay_height = screen_size[1]
        self.overlay_rect = pygame.Rect(-self.overlay_width, 0, self.overlay_width, self.overlay_height)  # start offscreen
        self.overlay_target_x = 0
        self.overlay_speed = 5 * self.overlay_width / 16  # Pixels per frame
        self.text_visible = False
        self.text_delay_counter = 0
        self.text_delay = 1  # frames
        self.current_card = None
        self.font = pygame.font.Font(None, GLOBAL_OVERLAY_FONT_SIZE)
        self.is_hovering = False

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

        match level:
            case 5:
                self.enemy_stack.insert(0, Enemy.Voldemort1())
            case 6:
                self.enemy_stack.insert(0, Enemy.Voldemort2())
            case 7:
                self.enemy_stack.insert(0, Enemy.Voldemort3())

        for enemy in self.open_enemies:
            if isinstance(enemy, Enemy.Basilisk) or isinstance(enemy, Enemy.Barty) or isinstance(enemy, Enemy.Greyback):
                self.game_state.permanent_modifiers.append(enemy.modifier)

        for _ in range(6):
            self.shop_cards.append(self.hogwarts_stack.pop())

        self.active_place = self.places.pop()

        for player in self.players:
            self.hands[player.name] = player.hand
            player.shuffle_deck()
            player.draw_5()

    def tick(self):
        game_state = self.game_state
        event_handler = game_state.event_handler

        self.overlay_tick()

        if event_handler.is_clicked["left"] and not event_handler.is_clicked_lock["left"]:
            if self.is_hovering:
                card = self.current_card
                if isinstance(card, Card.HogwartsCard):
                    if card in game_state.current_player.hand:
                        game_state.current_player.play_card(card, game_state)
                        game_state.card_position_manager.align_players()
                    if card in self.shop_cards:
                        game_state.current_player.buy_card(card, game_state)
                        game_state.card_position_manager.align_players()
                elif isinstance(card, Enemy.Enemy):
                    game_state.current_player.damage_enemy(card, game_state)

    def select_tick(self):
        game_state = self.game_state
        event_handler = game_state.event_handler

        self.overlay_tick()

        if event_handler.is_clicked["left"] and not event_handler.is_clicked_lock["left"]:
            for selectable in game_state.current_selection.selectables:
                if selectable.is_hovering(event_handler.mouse_pos):
                    game_state.current_selection.selections.append(selectable)
                    game_state.current_selection.amount -= 1
                    game_state.current_selection.selectables.remove(selectable)

    def overlay_tick(self):
        game_state = self.game_state
        event_handler = game_state.event_handler

        for card in self.shop_cards + [card for player in self.players for card in player.hand] + [player.discard_pile for player in self.players] + self.open_enemies + [self.dark_arts_dump, self.enemy_dump] + self.game_state.players + [self.enemy_stack]:
            is_hovering = card.is_hovering(event_handler.mouse_pos)

            if is_hovering:
                self.current_card = card
                if isinstance(card, Deck.DiscardPile):
                    if len(card) == 0:
                        self.is_hovering = False
                        break
                elif isinstance(card, Deck.Deck):
                    if not (len(card) == 1 and isinstance(card[0], Enemy.Voldemort)):
                        self.is_hovering = False
                        break

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

        self.enemy_stack.render(screen)
        self.hogwarts_stack.render(screen)
        self.active_place.render(screen)
        self.dark_arts_stack.render(screen)
        self.dark_arts_dump.render(screen)
        self.enemy_dump.render(screen)
        for shop_card in self.shop_cards:
            shop_card.render(screen)
        for enemy in self.open_enemies:
            enemy.render(screen)
        hand_cards = [card for player in self.players for card in player.hand]
        for card in hand_cards:
            card.render(screen)
        self.game_state.current_player.render_my_turn_overlay(screen)
        if self.game_state.current_selection:
            self.render_select_text(screen)
            self.game_state.current_selection.selector.render_selector_overlay(screen)
            for selectable in self.game_state.current_selection.selectables:
                selectable.render_select_overlay(screen)

        self.render_overlay(screen)

    def render_select_text(self, screen):
        text = self.game_state.current_selection.select_text
        space_width = self.game_state.card_position_manager.space_width
        space_height = self.game_state.card_position_manager.space_height
        space_pos = self.game_state.card_position_manager.space_pos

        text_height_portion = space_height * 19 // 48  # Calculate the height of the text area
        text_rect = pygame.Rect(space_pos[0], space_pos[1], space_width,
                                text_height_portion)  # Create the rectangle
        font = pygame.font.Font(None, 36)  # You can adjust the font size
        text_surface = font.render(text, True,  (255, 0, 0))
        text_rect = text_surface.get_rect(center=text_rect.center)
        screen.blit(text_surface, text_rect)

    def render_overlay(self, screen):
        s = pygame.Surface((self.overlay_rect.width, self.overlay_rect.height), pygame.SRCALPHA)  # per-pixel alpha
        s.fill((128, 128, 128, 128))  # values 0-255
        screen.blit(s, (self.overlay_rect.x, self.overlay_rect.y))

        if self.text_visible:
            reward_text = None
            card_name = ""
            card_description = ""
            if isinstance(self.current_card, Card.HogwartsCard):
                card_name = self.current_card.data["name"]
                card_description = self.current_card.data["description"]
            elif isinstance(self.current_card, Enemy.Enemy):
                card_name = self.current_card.name
                card_description = self.current_card.description
                reward_text = self.current_card.reward_text
            elif isinstance(self.current_card, Deck.DiscardPile) and len(self.current_card) > 0:
                card = self.current_card[len(self.current_card) - 1]
                if isinstance(card, Card.HogwartsCard) or isinstance(card, Card.DarkArtsCard):
                    card_name = card.data["name"]
                    card_description = card.data["description"]
                elif isinstance(card, Enemy.Enemy):
                    card_name = card.name
                    card_description = card.description
            elif isinstance(self.current_card, Player.Player):
                card_name = self.current_card.name
                if 3 <= self.game_state.level <= 6:
                    card_description = self.current_card.description1
                elif self.game_state.level == 7:
                    card_description = self.current_card.description2
            elif isinstance(self.current_card, Deck.Deck) and len(self.current_card) == 1 and isinstance(self.current_card[0], Enemy.Voldemort):
                card_name = self.current_card[0].name
                card_description = self.current_card[0].description
                reward_text = self.current_card[0].reward_text

            name_text = self.font.render(card_name, True, (0, 0, 0))
            name_rect = name_text.get_rect(center=(self.overlay_rect.centerx, self.overlay_rect.centery - 40))  # moved name up

            self.draw_multiline_text(screen, card_name, self.font, (0, 0, 0), name_rect)

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

    def draw_shop_cards(self):
        if not self.hogwarts_stack:
            return

        while len(self.shop_cards) < 6:
            if len(self.hogwarts_stack) > 0:
                self.shop_cards.append(self.hogwarts_stack.pop())

    def draw_enemies(self, amount):
        for _ in range(amount):
            self.draw_enemy()

    def draw_enemy(self):
        if not self.enemy_stack:
            return
        if len(self.enemy_stack) == 1 and isinstance(self.enemy_stack[0], Enemy.Voldemort) and self.open_enemies:
            return

        new_enemy = self.enemy_stack.pop()
        self.open_enemies.append(new_enemy)
        self.game_state.enemies_done[new_enemy] = False
        self.game_state.event_handler.dispatch_event(Event.EnemyDrawnEvent(new_enemy))

    def play_dark_arts(self, game_state):
        if not self.dark_arts_stack:
            self.reshuffle_dark_arts()

        dark_arts_card = self.dark_arts_stack.pop()
        dark_arts_card.play(None, game_state)
        self.dark_arts_dump.append(dark_arts_card)

    def reshuffle_dark_arts(self):
        if self.dark_arts_stack:
            raise Exception("Dark Arts Deck not empty, no shuffle needed!")

        self.dark_arts_stack.extend(self.dark_arts_dump)
        self.dark_arts_dump.clear()
        random.shuffle(self.dark_arts_stack)
