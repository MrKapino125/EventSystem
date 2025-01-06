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
    def __init__(self, event_handler: Eventhandler.EventHandler, players, level):
        super().__init__()
        self.event_handler = event_handler
        self.players = players
        self.level = level
        self.active_modifiers = []
        self.current_player = 0
        self.first_heal_given_this_turn = {}

    def start_turn(self, player):
        pass

    def end_turn(self, player):
        pass

    def add_modifier(self, modifier):
        self.active_modifiers.append(modifier)

    def remove_modifier(self, modifier):
        self.active_modifiers.remove(modifier)

    def apply_effect(self, effect, source, targets):
        for modifier in self.active_modifiers:
            effect = modifier.modify(effect)
            if effect is None:
                return  # Effect was cancelled
            # Apply the modified effect
        for target in targets:
            effect.apply(source, target, self)

    def handle_heal_event(self, event):
        source = event.data['source']
        target = event.data['target']
        amount = event.data['amount']

        if isinstance(self.players[self.current_player], Player.Neville):
            self.players[self.current_player].apply_hero_effect(event, self)

        target.apply_heal_effect(amount, self)

    def handle_damage_event(self, event):
        source = event.data['source']
        target = event.data['target']
        amount = event.data['amount']

        target.apply_damage_effect(amount, self)
