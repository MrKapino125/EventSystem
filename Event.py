class Event:
    def __init__(self, type, data=None):
        self.type = type
        self.data = data


class DrawCardEvent(Event):
    def __init__(self, source, target, amount):
        super().__init__("pre_draw_card", {"source": source, "target": target, "amount": amount})


class HealthGainedEvent(Event):
    def __init__(self, source, target, amount):
        super().__init__("health_gained", {"source": source, "target": target, "amount": amount})


class DamageTakenEvent(Event):
    def __init__(self, source, target, amount):
        super().__init__("damage_taken", {"source": source, "target": target, "amount": amount})
