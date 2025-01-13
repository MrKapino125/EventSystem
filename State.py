import Card
import Effect
import Enemy
import Eventhandler
import EffectModifiers
import Player
import Board
from CardPositionManager import CardPositionManager


class State:
    def __init__(self, state_manager):
        self.state_manager = state_manager

    def tick(self):
        pass

    def render(self, screen):
        pass


class GameState(State):
    def __init__(self, event_handler: Eventhandler.EventHandler, players_dict, level, state_manager):
        super().__init__(state_manager)
        self.event_handler = event_handler
        self.players_dict = players_dict
        self.players = list(players_dict.values())
        self.level = level
        self.active_modifiers = []
        self.current_player_idx = 0
        self.current_player = self.players[self.current_player_idx]
        self.hogwarts_cards, self.place_cards, self.dark_arts_cards = Card.load_cards(level)
        self.enemies = []

        self.init_decks()
        self.init_enemies()

        self.board = Board.Board(self.hogwarts_cards, self.dark_arts_cards, self.enemies, self.place_cards)
        self.board.setup(level)

        self.card_position_manager = CardPositionManager(self.players, self.board)
        self.card_position_manager.allign_shop_cards()

        self.valid_dice = []
        if self.level >= 4:
            self.valid_dice = ["gryffindor", "hufflepuff", "ravenclaw", "slytherin"]

    def tick(self):
        pass

    def render(self, screen):
        self.board.render(screen)
        for player in self.players:
            player.render_hand(screen)

    def init_decks(self):
        remaining_cards = []

        base_deck = [self.hogwarts_cards[0] for _ in range(7)]
        self.hogwarts_cards.pop(0)
        for player in self.players:
            player.deck = base_deck

        for card in self.hogwarts_cards:
            belonging = card.data.get("belonging")
            if belonging is None:
                remaining_cards.append(card)
            else:
                self.players_dict[belonging].deck.append(card)

        self.hogwarts_cards = remaining_cards

    def init_enemies(self):
        if self.level >= 1:
            self.enemies += [Enemy.Draco(), Enemy.CrabbeGoyle(), Enemy.Quirrell()]

    def start_turn(self, player):
        self.current_player = player

        dark_arts_cards = self.board.active_place.data['dark_arts_cards']
        for _ in range(dark_arts_cards):
            dark_arts_card = self.board.dark_arts_stack.pop()
            dark_arts_card.play()
            self.board.dark_arts_stack.append(dark_arts_card)

    def end_turn(self, player):
        pass

    def add_modifier(self, modifier):
        self.active_modifiers.append(modifier)

    def remove_modifier(self, modifier):
        self.active_modifiers.remove(modifier)

    def can_use_effect(self, effect, source, target):
        """Checks if an effect can be applied, considering modifiers."""
        modified_effect = effect
        for modifier in self.active_modifiers:
            modified_effect = modifier.modify(modified_effect, source, target, self)
            if modified_effect is None:
                return False  # Effect is blocked by a modifier
        return True  # Effect is allowed

    def apply_effect(self, effect, source, targets):
        for modifier in self.active_modifiers:
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

        if isinstance(self.current_player, Player.Hermione) and isinstance(card, Card.HogwartsCard):
            self.current_player.apply_hero_effect(event, self)

        for effect_data in card_data["effects"]:
            self._apply_card_effects(source, effect_data, card_data)

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

        target.apply_damage_effect(amount, self)

    def handle_remove_skull_event(self, event):
        source = event.data['source']
        amount = event.data['amount']

        if "Harry Potter" in self.existing_players:
            self.existing_players["Harry Potter"].apply_hero_effect(event, self)

        #remove skull from place

    def handle_bolt_given_event(self, event):
        target = event.data['target']
        amount = event.data['amount']

        self.current_player.apply_give_bolts_effect(amount, self)

    def handle_bolt_placed_event(self, event):
        target = event.data['target']
        amount = event.data['amount']

        if isinstance(self.current_player, Player.Ron):
            self.current_player.apply_hero_effect(event, self)

    def handle_coin_given_event(self, event):
        target = event.data['target']
        amount = event.data['amount']

        target.apply_give_coins_effect(amount, self)

    # PRIVATE #

    def _apply_card_effects(self, source, effect_data, card_data, active_player=None):
        effect_type = effect_data["type"]
        if active_player is None:
            active_player = self.current_player

        if effect_type == "choice":
            choice_targets_type = effect_data.get("choice_targets")
            if choice_targets_type is None:
                self._apply_effect_choice(active_player, source, effect_data, card_data)
            else:
                choice_targets = self._resolve_targets(active_player, choice_targets_type, None)
                for choice_target in choice_targets:
                    active_player = choice_target
                    self._apply_effect_choice(active_player, source, effect_data, card_data)
            return

        if effect_type == "give_coins":
            effect = Effect.GiveCoinsEffect(effect_data["amount"])
        elif effect_type == "heal":
            effect = Effect.HealEffect(effect_data["amount"])
        elif effect_type == "give_bolts":
            effect = Effect.GiveBoltEffect(effect_data["amount"])
        elif effect_type == "damage":
            effect = Effect.DamageEffect(effect_data["amount"])
        elif effect_type == "throw_dice":
            dice_type = effect_data["dice_type"]
            if effect_data["dice_type"] == "choice":
                effect = self.choose_dice(source)
            else:
                effect = self.get_effect_from_dice_type(dice_type)
        else:
            raise ValueError(f"Unknown effect type: {effect_type}")

        targets = self._resolve_targets(active_player, effect_data["target"], effect_data)

        self.apply_effect(effect, source, targets)

    def _apply_effect_choice(self, player, source, effect_data, card_data):
        description = card_data.get("description")
        num_effects = effect_data["num_effects"]
        options = effect_data["options"]

        print(f"{player.name}, choose {num_effects} effects:")

        if description is not None:
            options_desc = description.split(" oder ")
            for i, option in enumerate(options_desc):
                print(f"{i + 1}: {option}")

        chosen_effects = []
        while len(chosen_effects) < num_effects:
            while True:
                try:
                    choice = int(input("> ")) - 1
                    if 0 <= choice < len(options):
                        chosen_effects.append(options[choice])
                        break
                    else:
                        print("Invalid choice. Please try again.")
                except ValueError:
                    print("Invalid input. Please enter a number.")

        # Apply chosen effects
        for chosen_effect in chosen_effects:
            self._apply_card_effects(source, chosen_effect, card_data, player)

    def _resolve_targets(self, source, target_type, effect_data):
        if target_type == "self":
            return [source]
        elif target_type == "all":
            return self.players
        elif target_type == "choice":
            num_targets = effect_data.get("num_targets", 1)
            available_targets = effect_data.get("available_targets")
            valid_targets = self._resolve_available_targets(source, available_targets)
            if not valid_targets:
                return None
            chosen_targets = self.choose_targets(source, valid_targets, num_targets)
            return chosen_targets
        else:
            raise ValueError(f"Unknown target type: {target_type}")

    def _resolve_available_targets(self, source, available_targets_type):
        if available_targets_type == "all_players":
            return self.players
        elif available_targets_type == "other_players":
            return [p for p in self.players if p != source]
        elif available_targets_type is None:
            return self.players
        else:
            raise ValueError(f"Unknown target type: {available_targets_type}")

    # HELPER #

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


class StateManager:
    def __init__(self):
        self.current_state = None
        self.game_data = {}

    def switch_state(self, new_state, data=None):
        if data:
            self.game_data.update(data)
        self.current_state = new_state
