import selectors

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

        self.players_dict = players_dict
        self.players = list(players_dict.values())
        self.level = level
        self.screen_size = screen_size

        self.select = False
        self.selections_left = 0
        self.selection_callback = None
        self.selection_kwargs = {}
        self.selectors = []
        self.selectables = []
        self.selections = []
        self.current_selector = None
        self.select_text = ""

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
        if not self.select:
            self.regular_tick()
        else:
            self.select_tick()

    def regular_tick(self):
        if self.dark_arts_cards_left > 0:
            self.board.play_dark_arts(self)
            self.dark_arts_cards_left -= 1
            return

        for enemy, is_done in self.enemies_done.items():
            if not is_done:
                enemy.apply_effect(None, self)
                self.enemies_done[enemy] = True
                return

        if self.event_handler.is_clicked["left"] and not self.event_handler.is_clicked_lock["left"]:
            if self.end_turn_button.is_hovering(self.event_handler.mouse_pos):
                self.end_turn()
                return

        self.board.tick()

    def select_tick(self):
        if len(self.selectables) == 0 or self.selections_left == 0:
            self.selection_callback(**self.selection_kwargs)
            self.card_position_manager.realign_board()
            return

        self.board.select_tick()

    def render(self, screen):
        for player in self.players:
            player.render(screen)
        self.board.render(screen)
        self.end_turn_button.render(screen)

    def init_round(self):
        self.board.draw_shop_cards()
        while self.enemies_to_draw > 0:
            self.event_handler.dispatch_event(Event.EnemyDrawnEvent())

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

        self.init_round()

    def parse_modifier_type(self, modifier_type):
        if modifier_type == "no_draw":
            modifier = EffectModifiers.CantDrawCardsModifier()
        elif modifier_type == "no_heal":
            modifier = EffectModifiers.CantHealModifier()
        elif modifier_type == "one_bolt":
            modifier = EffectModifiers.OneBoltPerEnemyModifier()
        elif modifier_type[:3] == "buy":
            modifier = EffectModifiers.BuyCardModifier(modifier_type.split("_")[1])
        else:
            print("Unknown modifier type" + modifier_type)
            return None

        return modifier

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
            modified_effect = modifier.modify(modified_effect, source, target, self)
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

        if isinstance(self.current_player, Player.Hermione):
            self.current_player.apply_hero_effect(event, self)

        modifier_type_list = card_data.get("modifier")
        if modifier_type_list is not None:
            for modifier_type in modifier_type_list:
                modifier = self.parse_modifier_type(modifier_type)
                if modifier is not None:
                    self.add_modifier(modifier)

        for effect_data in card_data["effects"]:
            self._apply_card_effects(source, effect_data, card)

    def handle_dark_arts_card_played_event(self, event):
        source = event.data["source"]
        card = event.data["card"]
        card_data = card.data

        if card.data.get("is_unforgivable", False):
            self.dark_arts_cards_left += 1

        modifier_type_list = card_data.get("modifier")
        if modifier_type_list is not None:
            for modifier_type in modifier_type_list:
                modifier = self.parse_modifier_type(modifier_type)
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

        if isinstance(self.current_player, Player.Neville):
            self.current_player.apply_hero_effect(event, self)

        target.apply_heal_effect(amount, self)

    def handle_damage_event(self, event):
        source = event.data['source']
        target = event.data['target']
        amount = event.data['amount']

        if isinstance(source, Player.Player):
            source.bolts -= 1
        if isinstance(target, Enemy.Enemy):
            if isinstance(self.current_player, Player.Ron):
                self.current_player.apply_hero_effect(event, self)

        target.apply_damage_effect(amount, self, event)

    def handle_remove_skull_event(self, event):
        source = event.data['source']
        amount = event.data['amount']

        if "Harry Potter" in self.players_dict:
            self.players_dict["Harry Potter"].apply_hero_effect(event, self)

        self.board.active_place.remove_skulls(amount)

    def handle_add_skull_event(self, event):
        source = event.data['source']
        amount = event.data['amount']

        for enemy in self.board.open_enemies:
            if isinstance(enemy, Enemy.Draco):
                enemy.apply_effect(event, self)

        self.board.active_place.add_skulls(amount)

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

        open_enemies_left = [enemy for enemy in self.board.open_enemies if not enemy.is_dead and enemy != source]

        if len(open_enemies_left) + len(self.board.enemy_stack) == 0:
            self.win()
            return

        source.apply_reward(self)

    def handle_enemy_drawn_event(self, event):
        for enemy in self.board.open_enemies:
            if isinstance(enemy, Enemy.Todesser):
                enemy.apply_effect(event, self)

        self.board.draw_enemy()
        self.enemies_to_draw -= 1

    def handle_place_lost_event(self, event):
        if not self.board.places:
            self.lose()
            return

        self.board.active_place = self.board.places.pop()
        self.card_position_manager.realign_board()

    def handle_card_dropped_event(self, event):
        source = event.data['source']
        target = event.data['target']
        card = event.data['card']
        drop_effects = card.data.get("drop_effects")

        for enemy in self.board.open_enemies:
            if isinstance(enemy, Enemy.CrabbeGoyle):
                enemy.apply_effect(event, self)

        target.apply_drop_card_effect(event, self)
        if drop_effects is not None:
            for drop_effect in drop_effects:
                self._apply_card_effects(target, drop_effect, card)

    def handle_player_dead_event(self, event):
        source = event.data['source']
        target = event.data['target']

        self.board.active_place.add_skulls(1)
        if isinstance(source, Card.DarkArtsCard):
            if source.data["name"] == "AVADA KEDAVRA!":
                self.board.active_place.add_skulls(1)

        target.die(self, source)

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

        if effect_type == "give_coins":
            effect = Effect.GiveCoinsEffect(effect_data["amount"])
        elif effect_type == "heal":
            effect = Effect.HealEffect(effect_data["amount"])
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
        elif effect_type == "throw_dice":
            dice_type = effect_data["dice_type"]
            if effect_data["dice_type"] == "choice":
                effect = self.choose_dice(source)
            else:
                effect = self.get_effect_from_dice_type(dice_type)
        else:
            raise ValueError(f"Unknown effect type: {effect_type}")

        target_type = effect_data.get("target")
        if target_type is None:
            targets = [None]
        else:
            targets = self._resolve_targets(active_player, target_type, effect_data)

        if effect == "drop_cards":
            self.select_drop_cards(targets, effect_data.get("card_type"), effect_data.get("amount", 1), source)
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
        pass

    def lose(self):
        pass

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

    def init_choice(self, selectors, amount, kwargs, callback, selectables, select_text):
        self.select = True
        self.selectors = selectors[:]
        self.select_text = select_text

        if self.current_player in self.selectors:
            self.current_selector = self.current_player
        else:
            self.current_selector = selectors[0]

        self.selections_left = amount
        self.selection_kwargs = kwargs
        self.selection_callback = callback
        self.selectables = selectables[:]
        self.selections = []

    def resolve_choice(self):
        self.select = False
        self.selectors = []
        self.current_selector = None
        self.selections_left = 0
        self.selection_kwargs = {}
        self.selection_callback = None
        self.selectables = []
        self.select_text = ""

    def select_targets(self, selectors, amount, valid_targets, source, card, effect, callback):
        selectables = valid_targets

        select_text = ""
        if card is not None:
            select_text = card.data["description"]
        selection_kwargs = {"amount": amount, "valid_targets": valid_targets, "source": source, "card": card, "effect": effect}

        #print(selectors, amount, selection_kwargs, callback, selectables, select_text)
        self.init_choice(selectors, amount, selection_kwargs, callback, selectables, select_text)

    def select_effect(self, selectors, amount, options, source, card):
        buttons = []
        for option in options:
            button = Button.EffectButton(option)
            button.set_text()
            buttons.append(button)
        self.card_position_manager.align_buttons(buttons)

        kwargs = {"source": source, "amount": amount, "options": buttons[:], "card": card}
        callback = self._effect_choice_callback

        self.init_choice(selectors, amount, kwargs, callback, buttons, card.data["description"])

    def select_drop_cards(self, selectors, card_type, amount, source):
        selectables = []
        callback = self._drop_cards_callback
        selection_kwargs = {"source": source, "amount": amount, "card_type": card_type}

        if self.current_player in selectors:
            self.current_selector = self.current_player
        else:
            self.current_selector = selectors[0]

        if card_type is None:
            for card in self.current_selector.hand:
                selectables.append(card)
        else:
            for card in self.current_selector.hand:
                if card.data["type"] == card_type:
                    selectables.append(card)

        select_text = ""
        if isinstance(source, Card.Card):
            select_text = source.data["description"]
        self.init_choice(selectors, amount, selection_kwargs, callback, selectables, select_text)

    # CALLBACKS

    def _drop_cards_callback(self, source, amount, card_type):
        player = self.current_selector
        selections = self.selections
        for card in selections:
            self.apply_effect(Effect.DropCardEffect(card), source, [player])

        self.selectors.remove(self.current_selector)
        if self.selectors:
            self.select_drop_cards(self.selectors, card_type, amount, source)
        else:
            self.resolve_choice()

    def _effect_choice_callback(self, source, amount, options, card):
        selections = self.selections
        for button in selections:
            effect = button.effect
            self._apply_card_effects(source, effect, card, self.current_selector)

        if self.selection_callback == self._effect_choice_callback:
            self.selectors.remove(self.current_selector)
            if self.selectors:
                self.select_effect(self.selectors, amount, options, source, card)
            else:
                self.resolve_choice()

    def _select_player_callback(self, amount, valid_targets, source, card, effect):
        selections = self.selections
        for player in selections:
            self.apply_effect(effect, source, [player])

        self.selectors.remove(self.current_selector)
        if self.selectors:
            self.select_targets(selectors, amount, valid_targets, source, card, effect, self._select_player_callback)
        else:
            self.resolve_choice()


class StateManager:
    def __init__(self):
        self.current_state = None
        self.game_data = {}

    def switch_state(self, new_state, data=None):
        if data:
            self.game_data.update(data)
        self.current_state = new_state
