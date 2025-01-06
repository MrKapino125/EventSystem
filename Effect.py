import Event


class Effect:
    def apply(self, source, target, game_state):
        pass


class HealEffect(Effect):
    def __init__(self, amount):
        self.amount = amount

    def apply(self, source, target, game_state):
        game_state.event_handler.dispatch_event(Event.HealthGainedEvent(source, target, self.amount))


class DamageEffect(Effect):
    def __init__(self, amount):
        self.amount = amount

    def apply(self, source, target, game_state):
        game_state.event_handler.dispatch_event(Event.DamageTakenEvent(source, target, self.amount))


class DrawCardEffect(Effect):
    pass
