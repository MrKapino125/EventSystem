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


class CardDroppedEvent(Event):
    def __init__(self, source, target, card):
        super().__init__("card_dropped", {"source": source, "target": target, "card": card})


class CardDrawnEvent(Event):
    def __init__(self, source, target, amount):
        super().__init__("card_drawn", {"source": source, "target": target, "amount": amount})
