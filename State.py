import sys

import Card
import Deck
import Effect
import Enemy
import Event
import Eventhandler
import EffectModifiers
import Player
import Board
import Button
import pygame
from CardPositionManager import CardPositionManager


class State:
    def __init__(self, state_manager):
        self.state_manager = state_manager

    def tick(self):
        pass

    def render(self, screen):
        pass


class MenuState(State):
    def __init__(self, state_manager, event_handler, screen_size, players):
        super().__init__(state_manager)
        self.event_handler = event_handler
        self.event_handler.clear_listeners()
        self.selected_level = 1
        self.players = players
        self.screen_size = screen_size
        self.selected_players = []

        self.level_buttons = []
        for i in range(7):
            level = i+1
            button = Button.Button()
            button.width, button.height = self.screen_size[0] / 10, self.screen_size[0] / 10
            button.text = f'Level {level}'
            button.lines = button.generate_lines()
            self.level_buttons.append(button)
        self.level_buttons[0].selected = True

        self.player_buttons = []
        for i in range(4):
            button = Button.Button()
            button.width, button.height = self.screen_size[0] / 10, self.screen_size[0] / 6
            button.text = self.players[i].name
            button.lines = button.generate_lines()
            self.player_buttons.append(button)

        self.player_name_player_dict = dict(zip([player.name for player in self.players], self.players))

        self.submit_button = Button.Button()
        self.submit_button.width, self.submit_button.height = self.screen_size[0] / 20, self.screen_size[1] / 20
        self.submit_button.text = 'Start'
        self.submit_button.lines = self.submit_button.generate_lines()

        self.align_buttons()

    def tick(self):
        if self.event_handler.is_clicked["left"] and not self.event_handler.is_clicked_lock["left"]:
            for i, button in enumerate(self.level_buttons):
                if button.is_hovering(self.event_handler.mouse_pos):
                    self.level_buttons[self.selected_level - 1].selected = False
                    self.selected_level = i+1
                    button.selected = True

            for i, button in enumerate(self.player_buttons):
                if button.is_hovering(self.event_handler.mouse_pos):
                    if not button.selected:
                        button.selected = True
                        self.selected_players.append(self.player_name_player_dict[button.text])
                        break
                    else:
                        button.selected = False
                        self.selected_players.remove(self.player_name_player_dict[button.text])
                        break

            if self.submit_button.is_hovering(self.event_handler.mouse_pos) and len(self.selected_players) == 4:
                self.on_start_click()

    def render(self, screen):
        for button in self.level_buttons:
            button.render(screen)
        for button in self.player_buttons:
            button.render(screen)
            if button.selected:
                index = self.selected_players.index(self.player_name_player_dict[button.text])
                text_surface = button.font.render(f"{index + 1}.", True, (255, 0, 0))
                text_rect = text_surface.get_rect(center=(button.pos[0] + button.width // 2,
                                                          button.pos[1] + button.height - 20))  # vertical align
                screen.blit(text_surface, text_rect)
        self.submit_button.render(screen)

    def on_start_click(self):
        self.state_manager.switch_state(GameState(self.event_handler, dict(zip([player.name for player in self.selected_players], self.selected_players)), self.selected_level, self.state_manager, self.screen_size))

    def align_buttons(self):
        buttons = self.level_buttons
        screen_size = self.screen_size

        screen_width, screen_height = screen_size
        button_size = buttons[0].width

        # Calculate spacing (adjust as needed)
        horizontal_spacing_top = 25
        horizontal_spacing_bottom = horizontal_spacing_top
        vertical_spacing = 25

        initial_horizontal_top = (screen_width - (4 * button_size + 3 * horizontal_spacing_top)) / 2
        initial_horizontal_bottom = (screen_width - (3 * button_size + 2 * horizontal_spacing_bottom)) / 2


                                      # Position the top 4 buttons
        top_row_y = vertical_spacing / 2  # Corrected top row Y position
        for i in range(4):
            x = initial_horizontal_top + i * (button_size + horizontal_spacing_top)
            buttons[i].pos = (x, top_row_y)

        # Position the bottom 3 buttons
        bottom_row_y = top_row_y + button_size + 10  # Corrected bottom row Y position
        for i in range(3):
            x = initial_horizontal_bottom + i * (
                        button_size + horizontal_spacing_bottom)  # offset to center
            buttons[i + 4].pos = (x, bottom_row_y)

        buttons = self.player_buttons

        button_width = buttons[0].width
        button_height = buttons[0].height

        initial_horizontal = (screen_width - (4 * button_width + 3 * horizontal_spacing_top)) / 2

        row_y = bottom_row_y + button_size + 10 * vertical_spacing
        for i in range(4):
            x = initial_horizontal + i * (button_width + horizontal_spacing_top)
            buttons[i].pos = (x, row_y)

        submit_button_width = self.submit_button.width
        submit_button_height = self.submit_button.height

        submit_y = screen_height - (vertical_spacing + submit_button_height)
        submit_x = (screen_width - submit_button_width) / 2
        self.submit_button.pos = submit_x, submit_y


class GameState(State):
    def __init__(self, event_handler: Eventhandler.EventHandler, players_dict, level, state_manager, screen_size):
        super().__init__(state_manager)
        self.event_handler = event_handler
        event_handler.register_listener("damage_taken", self.handle_damage_event)
        event_handler.register_listener("health_gained", self.handle_heal_event)
        event_handler.register_listener("bolt_given", self.handle_bolt_given_event)
        event_handler.register_listener("coin_given", self.handle_coin_given_event)
        event_handler.register_listener("card_played", self.handle_card_played_event)
        event_handler.register_listener("card_drawn", self.handle_card_drawn_event)
        event_handler.register_listener("enemy_dead", self.handle_enemy_dead_event)
        event_handler.register_listener("skull_removed", self.handle_remove_skull_event)
        event_handler.register_listener("skull_placed", self.handle_add_skull_event)
        event_handler.register_listener("enemy_drawn", self.handle_enemy_drawn_event)
        event_handler.register_listener("place_lost", self.handle_place_lost_event)
        event_handler.register_listener("card_dropped", self.handle_card_dropped_event)
        event_handler.register_listener("player_dead", self.handle_player_dead_event)
        event_handler.register_listener("buy_card", self.handle_buy_card_event)
        event_handler.register_listener("reuse", self.handle_reuse_event)
        event_handler.register_listener("redraw", self.handle_redraw_event)
        event_handler.register_listener("draw_top", self.handle_draw_top_event)
        event_handler.register_listener("coins_health", self.handle_coins_health_event)

        self.players_dict = players_dict
        self.players = list(players_dict.values())
        self.level = level
        self.screen_size = screen_size

        self.select = False
        self.current_selection = None
        self.selection_pipeline = []

        self.end_turn_button = Button.Button()

        self.turn_started = False

        self.active_modifiers = []
        self.permanent_modifiers = []
        self.current_player_idx = 0
        self.current_player = self.players[self.current_player_idx]
        self.hogwarts_cards, self.place_cards, self.dark_arts_cards = Card.load_cards(level)
        self.enemies = []
        self.dark_arts_cards_left = 0
        self.enemies_to_draw = 0

        self.init_decks()
        self.init_enemies()

        self.board = Board.Board(self.hogwarts_cards, self.dark_arts_cards, self.enemies, self.place_cards, self.players, self)
        self.board.setup(level)

        self.board_pos = (0, 0)
        self.board_width = screen_size[0] // 2
        self.board_height = 3 * screen_size[1] // 4
        self.card_position_manager = CardPositionManager(self)
        self.card_position_manager.realign_board(self.board_pos, self.board_width, self.board_height)

        self.valid_dice = []
        if self.level >= 4:
            self.valid_dice = ["gryffindor", "hufflepuff", "ravenclaw", "slytherin"]

        self.enemies_done = dict(zip(self.board.open_enemies, [False for _ in range(len(self.board.open_enemies))]))

        self.init_round()

    def tick(self):
        if self.event_handler.is_clicked["middle"]:
            player1 = Player.Neville()
            player2 = Player.Harry()
            player3 = Player.Ron()
            player4 = Player.Hermione()
            players = [player1, player2, player3, player4]
            self.state_manager.switch_state(MenuState(self.state_manager, self.event_handler, self.screen_size, players))

        if not self.select:
            self.regular_tick()
        else:
            self.select_tick()

    def regular_tick(self):
        if self.selection_pipeline:
            self.select = True
            self.current_selection = self.selection_pipeline.pop(0)
            return

        if self.dark_arts_cards_left > 0:
            self.init_choice([self.current_player], 1, {}, self._select_dark_arts_callback, [self.board.dark_arts_stack], "Decke eine Dunkle Künste Karte auf!")
            return

        for enemy, is_done in self.enemies_done.items():
            if not is_done:
                if enemy.__class__._execute_active is Enemy.Enemy._execute_active or enemy.stunned:
                    self.enemies_done[enemy] = True
                else:
                    self.init_choice([self.current_player], 1, {"enemy": enemy}, self._select_enemy_callback,
                                 [enemy], "Aktiviere den Effekt des Bösewichts")
                return

        if self.event_handler.is_clicked["left"] and not self.event_handler.is_clicked_lock["left"]:
            if self.end_turn_button.is_hovering(self.event_handler.mouse_pos):
                self.end_turn()
                return

        self.board.tick()

    def select_tick(self):
        if not self.current_selection:
            self.select = False
            return
        if len(self.current_selection.selectables) == 0 or self.current_selection.amount == 0:
            self.current_selection.callback(**self.current_selection.kwargs)
            self.card_position_manager.realign_board()
            return

        self.board.select_tick()

    def render(self, screen):
        for player in self.players:
            player.render(screen)
        self.end_turn_button.render(screen)
        self.board.render(screen)

    def init_round(self):
        self.board.draw_shop_cards()
        while self.enemies_to_draw > 0:
            self.board.draw_enemy()
            self.enemies_to_draw -= 1

        self.dark_arts_cards_left = self.board.active_place.data['dark_arts_cards']
        for enemy in self.board.open_enemies:
            if isinstance(enemy, Enemy.Bellatrix):
                self.dark_arts_cards_left += 1

        self.card_position_manager.realign_board(self.board_pos, self.board_width, self.board_height)

    def init_decks(self):
        remaining_cards = []

        for player in self.players:
            player_deck = [Card.HogwartsCard(self.hogwarts_cards[0].data) for _ in range(7)]
            for card in player_deck:
                player.deck.append(card)
        self.hogwarts_cards.pop(0)

        for card in self.hogwarts_cards:
            belonging = card.data.get("belonging")
            if belonging is None:
                remaining_cards.append(card)
            else:
                self.players_dict[belonging].deck.append(card)

        self.hogwarts_cards = Deck.Deck()
        self.hogwarts_cards += remaining_cards

    def init_enemies(self):
        if self.level >= 1:
            self.enemies += [Enemy.Draco(), Enemy.CrabbeGoyle(), Enemy.Quirrell()]
        if self.level >= 2:
            self.enemies += [Enemy.Basilisk(), Enemy.Lucius(), Enemy.Riddle()]
        if self.level >= 3:
            self.enemies += [Enemy.Dementor(), Enemy.Pettigrew()]

        #self.enemies = [Enemy.Basilisk(), Enemy.CrabbeGoyle()]

    def end_turn(self):
        self.current_player.apply_end_turn_effect(self)

        if self.board.active_place.skulls == self.board.active_place.max_skulls:
            self.event_handler.dispatch_event(Event.PlaceLostEvent())

        enemies = []
        for enemy in self.board.open_enemies:
            if not enemy.is_dead:
                enemies.append(enemy)
            else:
                self.board.enemy_dump.append(enemy)
                self.enemies_to_draw += 1

        self.board.open_enemies.clear()
        self.board.open_enemies.extend(enemies)

        self.active_modifiers.clear()

        self.current_player_idx += 1
        self.current_player_idx %= len(self.players)
        self.current_player = self.players[self.current_player_idx]

        self.enemies_done = dict(zip(self.board.open_enemies, [False for _ in range(len(self.board.open_enemies))]))

        for player in self.players:
            if player.is_dead:
                player.is_dead = False
                player.health = 10

        for player in self.players:
            player.reset_effect()
        for enemy in self.board.open_enemies:
            enemy.apply_end_turn_effect(self)

        self.init_round()

    def parse_modifier_type(self, modifier_type, source):
        if modifier_type == "no_draw":
            modifier = EffectModifiers.CantDrawCardsModifier()
        elif modifier_type == "no_heal":
            modifier = EffectModifiers.CantHealModifier()
        elif modifier_type == "one_bolt_enemy":
            modifier = EffectModifiers.OneBoltPerEnemyModifier()
        elif modifier_type[:3] == "buy":
            modifier = EffectModifiers.BuyCardModifier(modifier_type.split("_")[1])
        elif modifier_type[:3] == "per":
            modifer_list = modifier_type.split("_")
            card_type = modifer_list[1]
            amount = int(modifer_list[2])
            effect_type = modifer_list[3]
            effect = self.parse_modifier_effect_type(effect_type, amount)
            modifier = EffectModifiers.EffectPerCardTypeModifier(effect, card_type, source, self)
        elif modifier_type[:11] == "first_enemy":
            modifier_list = modifier_type.split("_")
            amount = int(modifier_list[2])
            effect_type = modifier_list[3]
            effect = self.parse_modifier_effect_type(effect_type, amount)
            modifier = EffectModifiers.FirstEnemyKillModifier(effect, source, self)
        else:
            print("Unknown modifier type " + modifier_type)
            return None

        return modifier

    def parse_modifier_effect_type(self, modifier_effect_type, amount=1):
        if modifier_effect_type == "bolt":
            effect = Effect.GiveBoltEffect(amount)
        elif modifier_effect_type == "coin":
            effect = Effect.GiveCoinsEffect(amount)
        elif modifier_effect_type == "heal":
            effect = Effect.HealEffect(amount)
        else:
            raise ValueError("Unknown modifier effect type " + modifier_effect_type)

        return effect

    def add_modifier(self, modifier, permanent=False):
        if permanent:
            self.permanent_modifiers.append(modifier)
        else:
            self.active_modifiers.append(modifier)

    def remove_modifier(self, modifier, permanent=False):
        if permanent:
            self.permanent_modifiers.remove(modifier)
        else:
            self.active_modifiers.remove(modifier)

    def can_use_effect(self, effect, source, target):
        """Checks if an effect can be applied, considering modifiers."""
        modified_effect = effect
        for modifier in self.active_modifiers + self.permanent_modifiers:
            modified_effect = modifier.modify(modified_effect, self, source, [target])
            if modified_effect is None:
                return False  # Effect is blocked by a modifier
        return True  # Effect is allowed

    def apply_effect(self, effect, source, targets):
        for modifier in self.active_modifiers + self.permanent_modifiers:
            effect = modifier.modify(effect, self, source, targets)
            if effect is None:
                return  # Effect was cancelled
            # Apply the modified effect
        for target in targets:
            effect.apply(source, target, self)

    # EVENTHANDLER #

    def handle_card_played_event(self, event):
        source = event.data["source"]
        card = event.data["card"]
        card_data = card.data

        if isinstance(card, Card.HogwartsCard):
            self.handle_hogwarts_card_played_event(event)
        elif isinstance(card, Card.DarkArtsCard):
            self.handle_dark_arts_card_played_event(event)

    def handle_hogwarts_card_played_event(self, event):
        source = event.data["source"]
        card = event.data["card"]
        card_data = card.data

        modifier_type_list = card_data.get("modifier")
        if modifier_type_list is not None:
            for modifier_type in modifier_type_list:
                modifier = self.parse_modifier_type(modifier_type, source)
                if modifier is not None:
                    self.add_modifier(modifier)

        for effect_data in card_data["effects"]:
            self._apply_card_effects(source, effect_data, card)

        if isinstance(self.current_player, Player.Hermione) and card_data["type"] == "spell":
            self.current_player.apply_hero_effect(event, self)

    def handle_dark_arts_card_played_event(self, event):
        source = event.data["source"]
        card = event.data["card"]
        card_data = card.data

        if card.data.get("is_unforgivable", False):
            self.dark_arts_cards_left += 1

        modifier_type_list = card_data.get("modifier")
        if modifier_type_list is not None:
            for modifier_type in modifier_type_list:
                modifier = self.parse_modifier_type(modifier_type, source)
                if modifier is not None:
                    self.add_modifier(modifier)

        for effect_data in card_data["effects"]:
            self._apply_card_effects(source, effect_data, card)

    def handle_card_drawn_event(self, event):
        source = event.data["source"]
        target = event.data["target"]
        amount = event.data["amount"]

        target.apply_draw_card_effect(amount, self)
        self.card_position_manager.realign_board(self.board_pos, self.board_width, self.board_height)

    def handle_heal_event(self, event):
        source = event.data['source']
        target = event.data['target']
        amount = event.data['amount']

        health = target.health

        target.apply_heal_effect(amount, self)

        if isinstance(target, Player.Player):
            if isinstance(self.current_player, Player.Neville) and 0 < health < 10:
                self.current_player.apply_hero_effect(event, self)

    def handle_damage_event(self, event):
        source = event.data['source']
        target = event.data['target']
        amount = event.data['amount']

        if isinstance(target, Enemy.Enemy):
            if isinstance(self.current_player, Player.Ron):
                self.current_player.apply_hero_effect(event, self)

        target.apply_damage_effect(amount, self, event)

    def handle_remove_skull_event(self, event):
        source = event.data['source']
        amount = event.data['amount']

        skulls = self.board.active_place.skulls

        self.board.active_place.remove_skulls(amount)

        if "Harry Potter" in self.players_dict and skulls > 0:
            self.players_dict["Harry Potter"].apply_hero_effect(event, self)

    def handle_add_skull_event(self, event):
        source = event.data['source']
        amount = event.data['amount']

        self.board.active_place.add_skulls(amount)

        for enemy in self.board.open_enemies:
            if isinstance(enemy, Enemy.Draco):
                enemy.apply_effect(event, self)
            if isinstance(enemy, Enemy.Lucius):
                enemy.apply_effect(event, self)

    def handle_bolt_given_event(self, event):
        target = event.data['target']
        amount = event.data['amount']

        target.apply_give_bolts_effect(amount, self)

    def handle_coin_given_event(self, event):
        target = event.data['target']
        amount = event.data['amount']

        target.apply_give_coins_effect(amount, self)

    def handle_enemy_dead_event(self, event):
        source = event.data['source']
        target = event.data["target"]

        open_enemies_left = [enemy for enemy in self.board.open_enemies if not enemy.is_dead and enemy != target]
        del self.enemies_done[target]

        if len(open_enemies_left) + len(self.board.enemy_stack) == 0:
            self.win()
            return

        target.apply_reward(self)

    def handle_enemy_drawn_event(self, event):
        enemy = event.data["enemy"]

        if isinstance(enemy, Enemy.Basilisk) or isinstance(enemy, Enemy.Barty) or isinstance(enemy, Enemy.Greyback):
            self.permanent_modifiers.append(enemy.modifier)

        for enemy in self.board.open_enemies:
            if isinstance(enemy, Enemy.Todesser):
                enemy.apply_effect(event, self)

    def handle_place_lost_event(self, event):
        if not self.board.places:
            self.lose()
            return

        self.board.place_dump.append(self.board.active_place)
        self.board.active_place = self.board.places.pop()
        self.card_position_manager.realign_board()

    def handle_card_dropped_event(self, event):
        source = event.data['source']
        target = event.data['target']
        card = event.data['card']
        drop_effects = card.data.get("drop_effects")

        target.apply_drop_card_effect(event, self)
        if drop_effects is not None:
            for drop_effect in drop_effects:
                self._apply_card_effects(target, drop_effect, card, target)

        for enemy in self.board.open_enemies:
            if isinstance(enemy, Enemy.CrabbeGoyle):
                enemy.apply_effect(event, self)

        if isinstance(source, Player.Player):
            if source.cards_played:
                last_played = source.cards_played[-1]
                if last_played.data["name"] == "Sybill Trelawney":
                    if card.data["type"] == "spell":
                        self.apply_effect(Effect.GiveCoinsEffect(2), source, [target])

    def handle_player_dead_event(self, event):
        source = event.data['source']
        target = event.data['target']

        target.die(self, source)

        self.apply_effect(Effect.PlaceSkullEffect(1), source, [None])
        if isinstance(source, Card.DarkArtsCard):
            if source.data["name"] == "AVADA KEDAVRA!":
                self.apply_effect(Effect.PlaceSkullEffect(1), source, [None])

    def handle_buy_card_event(self, event):
        source = event.data['source']
        card = event.data['card']

        for modifier in self.active_modifiers:
            if isinstance(modifier, EffectModifiers.BuyCardModifier):
                if card.data["type"] == modifier.card_type:
                    source.deck.append(card)
                    break
        else:
            source.discard_pile.append(card)

        cost = card.data["cost"]
        source.coins -= cost
        self.board.shop_cards.remove(card)

    def handle_reuse_event(self, event):
        source = event.data['source']
        target = event.data['target']
        amount = event.data['amount']
        card_type = event.data['card_type']
        select_text = event.data["select_text"]

        options = []
        for card in target.cards_played:
            if card.data["type"] == card_type:
                options.append(card)

        self.select_card([target], amount, options, source, select_text, True)

    def handle_redraw_event(self, event):
        source = event.data['source']
        target = event.data['target']
        amount = event.data['amount']
        card_type = event.data['card_type']
        select_text = event.data["select_text"]

        options = []
        for card in target.discard_pile:
            if card.data["type"] == card_type:
                options.append(card)

        self.select_card([target], amount, options, source, select_text, False)

    def handle_draw_top_event(self, event):
        source = event.data['source']
        target = event.data['target']
        card_type = event.data['card_type']

        if not target.deck:
            return

        if card_type == "value":
            if target.deck[-1].data["cost"] > 0:
                card = target.deck.pop()
                target.hand.append(card)
                self.event_handler.dispatch_event(Event.CardDroppedEvent(source, target, card))
                self.apply_effect(Effect.DamageEffect(2), source, [target])
        else:
            if target.deck[-1].data["type"] == card_type:
                card = target.deck.pop()
                target.hand.append(card)
                self.event_handler.dispatch_event(Event.CardDroppedEvent(source, target, card))
                self.apply_effect(Effect.DamageEffect(2), source, [target])

    def handle_coins_health_event(self, event):
        source = event.data['source']
        target = event.data['target']
        amount = event.data['amount']

        self.apply_effect(Effect.HealEffect(amount), source, [target])
        self.apply_effect(Effect.GiveCoinsEffect(amount), source, [target])

    # PRIVATE #

    def _apply_card_effects(self, source, effect_data, card, active_player=None):
        if effect_data is None:
            return

        effect_type = effect_data["type"]
        if active_player is None:
            active_player = self.current_player

        if effect_type == "choice":
            choice_targets_type = effect_data.get("choice_targets")
            if choice_targets_type is None:
                self._apply_effect_choice([active_player], source, effect_data, card)
            else:
                choice_targets = self._resolve_targets(active_player, choice_targets_type, None)
                self._apply_effect_choice(choice_targets, source, effect_data, card)
            return

        effect = self.get_effect_from_type(effect_type, effect_data, card)

        target_type = effect_data.get("target")
        if target_type is None:
            targets = [None]
        else:
            targets = self._resolve_targets(active_player, target_type, effect_data)

        if effect == "drop_cards":
            self.select_drop_cards(targets, effect_data.get("card_type"), effect_data.get("amount", 1), source)
            return

        if effect == "stun":
            self.select_stun(active_player, card.data["description"])
            return

        if targets == "choice":
            num_targets = effect_data.get("num_targets", 1)
            available_targets = effect_data.get("available_targets")
            valid_targets = self._resolve_available_targets(source, available_targets)
            if not valid_targets:
                return None
            self.select_targets([active_player], num_targets, valid_targets, source, card, effect, self._select_player_callback)
            return

        self.apply_effect(effect, source, targets)

    def get_effect_from_type(self, effect_type, effect_data, card=None):
        if effect_type == "give_coins":
            effect = Effect.GiveCoinsEffect(effect_data["amount"])
        elif effect_type == "heal":
            effect = Effect.HealEffect(effect_data["amount"])
        elif effect_type == "give_coins_and_heal":
            effect = Effect.GiveCoinsHealEffect(effect_data["amount"])
        elif effect_type == "give_bolts":
            effect = Effect.GiveBoltEffect(effect_data["amount"])
        elif effect_type == "damage":
            effect = Effect.DamageEffect(effect_data["amount"])
        elif effect_type == "draw_cards":
            effect = Effect.DrawCardEffect(effect_data["amount"])
        elif effect_type == "remove_skulls":
            effect = Effect.RemoveSkullEffect(effect_data["amount"])
        elif effect_type == "place_skulls":
            effect = Effect.PlaceSkullEffect(effect_data["amount"])
        elif effect_type == "drop_cards":
            effect = "drop_cards"
        elif effect_type == "draw_top":
            effect = Effect.DrawTopEffect(effect_data["card_type"])
        elif effect_type == "stun":
            effect = "stun"
        elif effect_type[:5] == "reuse":
            select_text = ""
            if card is not None:
                select_text = card.data["description"]
            effect = Effect.ReUseEffect(effect_data["amount"], effect_type.split("_")[1], select_text)
        elif effect_type[:6] == "redraw":
            select_text = ""
            if card is not None:
                select_text = card.data["description"]
            effect = Effect.ReDrawEffect(effect_data["amount"], effect_type.split("_")[1], select_text)
        elif effect_type == "throw_dice":
            raise ValueError("throw_dice")
        else:
            raise ValueError(f"Unknown effect type: {effect_type}")

        return effect

    def _apply_effect_choice(self, choice_targets, source, effect_data, card):
        card_data = card.data
        description = card_data.get("description")
        num_effects = effect_data["num_effects"]
        options = effect_data["options"]

        self.select_effect(choice_targets, num_effects, options, source, card)

    def _resolve_targets(self, source, target_type, effect_data):
        if target_type == "self":
            return [source]
        elif target_type == "all":
            return self.players[:]
        elif target_type == "choice":
            return "choice"
        else:
            raise ValueError(f"Unknown target type: {target_type}")

    def _resolve_available_targets(self, source, available_targets_type):
        if available_targets_type == "all":
            return self.players
        elif available_targets_type == "other":
            return [p for p in self.players if p != source]
        elif available_targets_type is None:
            return self.players
        else:
            raise ValueError(f"Unknown target type: {available_targets_type}")

    # HELPER #

    def win(self):
        print("You Win!")
        self.show_stats()
        pygame.quit()
        sys.exit(0)

    def lose(self):
        print("You Lose!")
        self.show_stats()
        pygame.quit()
        sys.exit(0)

    def show_stats(self):
        print("----------------------------------------------------------------")
        print("Decks:")
        for player in self.players:
            print(f"{player.name} deck: {player.deck + player.hand + player.discard_pile}")

        print("----------------------------------------------------------------")
        print("Places:")
        for place in self.board.place_dump + [self.board.active_place] + self.board.places:
            print(place)

        print("----------------------------------------------------------------")
        print("Enemies:")
        for enemy in self.board.enemy_dump + self.board.open_enemies + self.board.enemy_stack:
            print(enemy)

    def get_available_targets_for_effect(self, effect, source, possible_targets=None):
        available_targets = []
        if possible_targets is None:
            possible_targets = self.players
        for target in possible_targets:
            if self.can_use_effect(effect, source, target):
                available_targets.append(target)

        return available_targets

    def select_single_target(self, player, valid_targets=None):
        """Prompts the player to select a single target."""
        if valid_targets is None:
            valid_targets = self.players  # Default is all players

        print(f"{player.name}, choose a target:")
        for i, target in enumerate(valid_targets):
            print(f"{i + 1}: {target.name}")

        while True:
            try:
                choice = int(input("> ")) - 1
                if 0 <= choice < len(valid_targets):
                    return valid_targets[choice]
                else:
                    print("Invalid choice. Please try again.")
            except ValueError:
                print("Invalid input. Please enter a number.")

    def select_multiple_targets(self, player, num_targets, valid_targets=None):
        """Prompts the player to select multiple targets."""
        if valid_targets is None:
            valid_targets = self.players  # Default is all players
        if num_targets > len(valid_targets):
            num_targets = len(valid_targets)
        selected_targets = []
        print(f"{player.name}, choose {num_targets} targets:")
        for i, target in enumerate(valid_targets):
            print(f"{i + 1}: {target.name}")

        while len(selected_targets) < num_targets:
            try:
                choice = int(input("> ")) - 1
                if 0 <= choice < len(valid_targets):
                    target = valid_targets[choice]
                    if target in selected_targets:
                        print("You have already selected that target. Please choose a different one.")
                    else:
                        selected_targets.append(target)
                else:
                    print("Invalid choice. Please try again.")
            except ValueError:
                print("Invalid input. Please enter a number.")
        return selected_targets

    def get_effect_from_dice_type(self, dice_type):
        match dice_type:
            case "gryffindor":
                return Effect.ThrowGryffindorEffect()
            case "hufflepuff":
                return Effect.ThrowHufflepuffEffect()
            case "ravenclaw":
                return Effect.ThrowRavenclawEffect()
            case "slytherin":
                return Effect.ThrowSlytherinEffect()
            case _:
                raise ValueError(f"Unknown dice type: {dice_type}")

    def choose_dice(self, source):
        print(f"{source.name}, choose a dice:")
        for i, dice in enumerate(self.valid_dice):
            print(f"{i + 1}: {dice}")

        while True:
            try:
                choice = int(input("> ")) - 1
                if 0 <= choice < len(self.valid_dice):
                    return self.get_effect_from_dice_type(self.valid_dice[choice])
                else:
                    print("Invalid choice. Please try again.")
            except ValueError:
                print("Invalid input. Please enter a number.")

    def choose_targets(self, source, valid_targets, num_targets):
        if num_targets == 1:
            return [self.select_single_target(source, valid_targets)]
        else:
            return self.select_multiple_targets(source, num_targets, valid_targets)

    def init_choice(self, selectors, amount, kwargs, callback, selectables, select_text, prio=True):
        _selectors = selectors[:]
        self.select = True
        if prio:
            _selectors.reverse()

        for selector in _selectors:
            select_object = SelectionObject(selector, amount, kwargs, callback, selectables[:], select_text)
            if prio:
                self.selection_pipeline.insert(0, select_object)
            else:
                self.selection_pipeline.append(select_object)

    def resolve_choice(self):
        self.select = False
        self.current_selection = None

    def select_targets(self, selectors, amount, valid_targets, source, card, effect, callback):
        selectables = valid_targets

        select_text = ""
        if card is not None:
            select_text = card.data["description"]
        selection_kwargs = {"amount": amount, "valid_targets": valid_targets, "source": source, "card": card, "effect": effect}

        #print(selectors, amount, selection_kwargs, callback, selectables, select_text)
        self.init_choice(selectors, amount, selection_kwargs, callback, selectables, select_text)

    def select_effect(self, selectors, amount, options, source, card, callback=None):
        buttons = []
        for option in options:
            button = Button.EffectButton(option)
            button.set_text()
            buttons.append(button)
        self.card_position_manager.align_buttons(buttons)

        kwargs = {"source": source, "amount": amount, "options": options, "card": card}
        if callback is None:
            callback = self._effect_choice_callback

        for selector in selectors:
            selectables = buttons[:]
            for button in buttons:
                if button.effect["type"] == "drop_cards":
                    if button.effect.get("card_type") is not None:
                        if not [card for card in selector.hand if card.data["type"] == button.effect["card_type"]]:
                            selectables = [s for s in selectables if s != button]

            self.init_choice([selector], amount, kwargs, callback, selectables, card.data["description"], False)

    def select_card(self, selectors, amount, options, source, select_text, insta_use):
        buttons = []
        for option in options:
            button = Button.CardButton(option)
            button.set_text()
            buttons.append(button)
        self.card_position_manager.align_buttons(buttons)

        kwargs = {"source": source, "amount": amount, "options": options, "insta_use": insta_use}
        callback = self._card_choice_callback

        self.init_choice(selectors, amount, kwargs, callback, buttons, select_text)

    def select_drop_cards(self, selectors, card_type, amount, source, callback=None):
        if callback is None:
            callback = self._drop_cards_callback
        selection_kwargs = {"source": source, "amount": amount, "card_type": card_type}

        select_text = ""
        if isinstance(source, Card.Card):
            select_text = source.data["description"]

        for selector in selectors:
            selectables = []
            if card_type is None:
                for card in selector.hand:
                    selectables.append(card)
            else:
                for card in selector.hand:
                    if card.data["type"] == card_type:
                        selectables.append(card)

            self.init_choice([selector], amount, selection_kwargs, callback, selectables, select_text)

    def select_stun(self, selector, select_text):
        select_text = select_text

        selectables = self.board.open_enemies
        self.init_choice([selector], 1, {}, self._stun_callback, selectables, select_text)

    # CALLBACKS

    def _stun_callback(self):
        selections = self.current_selection.selections
        self.resolve_choice()

        for enemy in selections:
            enemy.stun(self)

    def _drop_cards_callback(self, source, amount, card_type):
        player = self.current_selection.selector
        selections = self.current_selection.selections
        for card in selections:
            self.apply_effect(Effect.DropCardEffect(card), source, [player])

        self.resolve_choice()

    def _effect_choice_callback(self, source, amount, options, card):
        selections = self.current_selection.selections
        for button in selections:
            effect = button.effect
            self._apply_card_effects(source, effect, card, self.current_selection.selector)

        self.resolve_choice()

    def _card_choice_callback(self, source, amount, options, insta_use):
        selections = self.current_selection.selections
        for button in selections:
            card = button.card
            if insta_use:
                card.play(self.current_selection.selector, self)
                self.current_selection.selector.cards_played.append(card)
            else:
                self.current_selection.selector.discard_pile.remove(card)
                self.current_selection.selector.hand.append(card)

        self.resolve_choice()

    def _select_player_callback(self, amount, valid_targets, source, card, effect):
        selections = self.current_selection.selections
        for player in selections:
            self.apply_effect(effect, source, [player])

        self.resolve_choice()

    def _select_dark_arts_callback(self):
        self.board.play_dark_arts(self)
        self.dark_arts_cards_left -= 1

        self.resolve_choice()

    def _select_enemy_callback(self, enemy):
        enemy.apply_effect(None, self)
        self.enemies_done[enemy] = True

        self.resolve_choice()


class StateManager:
    def __init__(self):
        self.current_state = None
        self.game_data = {}

    def switch_state(self, new_state, data=None):
        if data:
            self.game_data.update(data)
        self.current_state = new_state


class SelectionObject:
    def __init__(self, selector, amount, kwargs, callback, selectables, select_text):
        self.selector = selector
        self.amount = amount
        self.kwargs = kwargs
        self.callback = callback
        self.selectables = selectables
        self.select_text = select_text
        self.selections = []

    def __repr__(self):
        return self.selector.name

