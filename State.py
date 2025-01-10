import Effect
import Eventhandler
import EffectModifiers
import Player


class State:
    def __init__(self):
        pass

    def tick(self):
        pass

    def render(self):
        pass


class GameState(State):
    def __init__(self, event_handler: Eventhandler.EventHandler, players: list, level):
        super().__init__()
        self.event_handler = event_handler
        self.players = players
        self.level = level
        self.active_modifiers = []
        self.current_player_idx = 0
        self.current_player = players[self.current_player_idx]
        self.first_heal_given_this_turn = {}
        self.valid_dice = []
        if self.level >= 4:
            self.valid_dice = ["gryffindor", "hufflepuff", "ravenclaw", "slytherin"]
        if self.level >= 9:
            self.valid_dice.append("monster")

    def start_turn(self, player):
        pass

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
        card_data = event.data["card_data"]

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

        if isinstance(self.current_player, Player.Harry):
            self.current_player.apply_hero_effect(event, self)

        #remove skull from place

    def handle_bolt_given_event(self, event):
        target = event.data['target']
        amount = event.data['amount']

        self.current_player.apply_give_bolts_effect(amount, self)

    def handle_bolt_placed_event(self, event):
        target = event.data['target']
        amount = event.data['amount']

    def handle_coin_given_event(self, event):
        target = event.data['target']
        amount = event.data['amount']

        target.apply_give_coins_effect(amount, self)

    # PRIVATE #

    def _apply_card_effects(self, source, effect_data, card_data):
        effect_type = effect_data["type"]

        if effect_type == "choice":
            self._apply_effect_choice(source, effect_data, card_data)
            return

        if effect_type == "give_coins":
            effect = Effect.GiveCoinsEffect(effect_data["amount"])
        elif effect_type == "heal":
            effect = Effect.HealEffect(effect_data["amount"])
        elif effect_type == "give_bolts":
            effect = Effect.GiveBoltEffect(effect_data["amount"])
        elif effect_type == "throw_dice":
            dice_type = effect_data["dice_type"]
            if effect_data["dice_type"] == "choice":
                effect = self.choose_dice(source)
            else:
                effect = self.get_effect_from_dice_type(dice_type)
        else:
            raise ValueError(f"Unknown effect type: {effect_type}")

        targets = self._resolve_targets(source, effect_data["target"], effect_data)

        self.apply_effect(effect, source, targets)

    def _apply_effect_choice(self, source, effect_data, card_data):
        description = card_data.get("description")
        num_effects = effect_data["num_effects"]
        options = effect_data["options"]

        print(f"{source.name}, choose {num_effects} effects:")

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
            self._apply_card_effects(source, chosen_effect, card_data)

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
