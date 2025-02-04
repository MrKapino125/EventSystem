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
        game_state.event_handler.dispatch_event(Event.CardDrawnEvent(source, target, self.amount))


class GiveBoltEffect(Effect):
    def __init__(self, amount):
        self.amount = amount

    def apply(self, source, target, game_state):
        game_state.event_handler.dispatch_event(Event.BoltGivenEvent(source, target, self.amount))


class GiveCoinsEffect(Effect):
    def __init__(self, amount):
        self.amount = amount

    def apply(self, source, target, game_state):
        game_state.event_handler.dispatch_event(Event.CoinGivenEvent(source, target, self.amount))


class CardPlayEffect(Effect):
    def __init__(self, card, amount=1):
        self.card = card
        self.amount = amount

    def apply(self, source, target, game_state):
        game_state.event_handler.dispatch_event(Event.CardPlayedEvent(source, self.card, self.amount))


class EnemyDeadEffect(Effect):
    def apply(self, source, target, game_state):
        game_state.event_handler.dispatch_event(Event.EnemyDeadEvent(source, target))


class PlaceSkullEffect(Effect):
    def __init__(self, amount):
        self.amount = amount

    def apply(self, source, target, game_state):
        game_state.event_handler.dispatch_event(Event.SkullPlacedEvent(source, self.amount))


class RemoveSkullEffect(Effect):
    def __init__(self, amount):
        self.amount = amount

    def apply(self, source, target, game_state):
        game_state.event_handler.dispatch_event(Event.SkullRemovedEvent(source, self.amount))


class DropCardsEffect(Effect):
    def __init__(self, amount, card_type):
        self.amount = amount
        self.card_type = card_type

    def apply(self, source, target, game_state):
        game_state.event_handler.dispatch_event(Event.CardDropEvent(source, target, self.amount, self.card_type))


class DropCardEffect(Effect):
    def __init__(self, card):
        self.card = card

    def apply(self, source, target, game_state):
        game_state.event_handler.dispatch_event(Event.CardDroppedEvent(source, target, self.card))


class ReUseEffect(Effect):
    def __init__(self, amount, card_type, select_text=""):
        self.amount = amount
        self.card_type = card_type
        self.select_text = select_text

    def apply(self, source, target, game_state):
        game_state.event_handler.dispatch_event(Event.ReUseEvent(source, target, self.amount, self.card_type, self.select_text))


class ReDrawEffect(Effect):
    def __init__(self, amount, card_type, select_text=""):
        self.amount = amount
        self.card_type = card_type
        self.select_text = select_text

    def apply(self, source, target, game_state):
        game_state.event_handler.dispatch_event(Event.ReDrawEvent(source, target, self.amount, self.card_type, self.select_text))


class ThrowGryffindorEffect:
    pass


class ThrowHufflepuffEffect:
    pass


class ThrowRavenclawEffect:
    pass


class ThrowSlytherinEffect:
    pass
