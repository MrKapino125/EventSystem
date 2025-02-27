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


class GiveCoinsHealEffect(Effect):
    def __init__(self, amount):
        self.amount = amount

    def apply(self, source, target, game_state):
        game_state.event_handler.dispatch_event(Event.CoinsHealthGivenEvent(source, target, self.amount))


class GiveCoinsDrawEffect(Effect):
    def __init__(self, amount):
        self.amount = amount

    def apply(self, source, target, game_state):
        game_state.event_handler.dispatch_event(Event.CoinsDrawGivenEvent(source, target, self.amount))


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


class DrawTopEffect(Effect):
    def __init__(self, card_type):
        self.card_type = card_type

    def apply(self, source, target, game_state):
        game_state.event_handler.dispatch_event(Event.DrawTopEvent(source, target, self.card_type))


class ThrowDiceEffect(Effect):
    def __init__(self, dice_type, amount, is_evil):
        self.dice_type = dice_type
        self.amount = amount
        self.is_evil = is_evil

    def apply(self, source, target, game_state):
        game_state.event_handler.dispatch_event(Event.ThrowDiceEvent(source, target, self.dice_type, self.amount, self.is_evil))


class CheckHandEffect(Effect):
    def __init__(self):
        pass

    def apply(self, source, target, game_state):
        game_state.event_handler.dispatch_event(Event.CheckHandEvent(source, target))


class WeasleyEffect(Effect):
    def __init__(self, effect_type, amount, target_type):
        self.effect_type = effect_type
        self.effect_amount = amount
        self.effect_target_type = target_type

    def apply(self, source, target, game_state):
        game_state.event_handler.dispatch_event(Event.WeasleyEvent(source, target, self.effect_type, self.effect_amount, self.effect_target_type))
