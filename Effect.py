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
    def __init__(self, amount):
        self.amount = amount

    def apply(self, source, target, game_state):
        pass


class GiveBoltEffect(Effect):
    def __init__(self, amount):
        self.amount = amount

    def apply(self, source, target, game_state):
        game_state.event_handler.dispatch_event(Event.BoltGivenEvent(source, target, self.amount))


class PlaceBoltEffect(Effect):
    def __init__(self, amount):
        self.amount = amount

    def apply(self, source, target, game_state):
        pass


class GiveCoinsEffect(Effect):
    def __init__(self, amount):
        self.amount = amount

    def apply(self, source, target, game_state):
        game_state.event_handler.dispatch_event(Event.CoinGivenEvent(source, target, self.amount))


class CardPlayEffect(Effect):
    def __init__(self, card):
        self.card = card

    def apply(self, source, target, game_state):
        game_state.event_handler.dispatch_event(Event.CardPlayedEvent(source, self.card))


class ThrowGryffindorEffect:
    pass


class ThrowHufflepuffEffect:
    pass


class ThrowRavenclawEffect:
    pass


class ThrowSlytherinEffect:
    pass
