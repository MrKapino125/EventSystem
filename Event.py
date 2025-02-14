class Event:
    def __init__(self, type, data=None):
        self.type = type
        self.data = data


class HealthGainedEvent(Event):
    def __init__(self, source, target, amount):
        super().__init__("health_gained", {"source": source, "target": target, "amount": amount})


class DamageTakenEvent(Event):
    def __init__(self, source, target, amount):
        super().__init__("damage_taken", {"source": source, "target": target, "amount": amount})


class BoltGivenEvent(Event):
    def __init__(self, source, target, amount):
        super().__init__("bolt_given", {"source": source, "target": target, "amount": amount})


class BoltPlacedEvent(Event):
    def __init__(self, source, target, amount):
        super().__init__("bolt_placed", {"source": source, "target": target, "amount": amount})


class CoinGivenEvent(Event):
    def __init__(self, source, target, amount):
        super().__init__("coin_given", {"source": source, "target": target, "amount": amount})


class CardPlayedEvent(Event):
    def __init__(self, source, card, amount=1):
        super().__init__("card_played", {"source": source, "card": card, "amount": amount})


class SkullPlacedEvent(Event):
    def __init__(self, source, amount):
        super().__init__("skull_placed", {"source": source, "amount": amount})


class SkullRemovedEvent(Event):
    def __init__(self, source, amount):
        super().__init__("skull_removed", {"source": source, "amount": amount})


class CardDropEvent(Event):
    def __init__(self, source, target, amount, card_type):
        super().__init__("card_drop", {"source": source, "target": target, "amount": amount, card_type: card_type})


class CardDroppedEvent(Event):
    def __init__(self, source, target, card):
        super().__init__("card_dropped", {"source": source, "target": target, "card": card})


class CardDrawnEvent(Event):
    def __init__(self, source, target, amount):
        super().__init__("card_drawn", {"source": source, "target": target, "amount": amount})


class EnemyDeadEvent(Event):
    def __init__(self, source, target):
        super().__init__("enemy_dead", {"source": source, "target": target})


class EnemyDrawnEvent(Event):
    def __init__(self):
        super().__init__("enemy_drawn", {})


class PlaceLostEvent(Event):
    def __init__(self):
        super().__init__("place_lost", {})


class PlayerDeadEvent(Event):
    def __init__(self, source, target):
        super().__init__("player_dead", {"source": source, "target": target})


class BuyCardEvent(Event):
    def __init__(self, source, card):
        super().__init__("buy_card", {"source": source, "card": card})


class ReUseEvent(Event):
    def __init__(self, source, target, amount, card_type, select_text=""):
        super().__init__("reuse", {"source": source, "target": target, "amount": amount, "card_type": card_type, "select_text": select_text})


class ReDrawEvent(Event):
    def __init__(self, source, target, amount, card_type, select_text=""):
        super().__init__("redraw", {"source": source, "target": target, "amount": amount, "card_type": card_type, "select_text": select_text})


class DrawTopEvent(Event):
    def __init__(self, source, target, card_type):
        super().__init__("draw_top", {"source": source, "target": target, "card_type": card_type})


class CoinsHealthGivenEvent(Event):
    def __init__(self, source, target, amount):
        super().__init__("coins_health", {"source": source, "target": target, "amount": amount})
