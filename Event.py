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
    def __init__(self, source, card_data, amount=1):
        super().__init__("card_played", {"source": source, "card_data": card_data, "amount": amount})
