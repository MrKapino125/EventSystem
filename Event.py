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
    def __init__(self, source, target, card, is_death=False):
        super().__init__("card_dropped", {"source": source, "target": target, "card": card, "is_death": is_death})


class CardDrawnEvent(Event):
    def __init__(self, source, target, amount):
        super().__init__("card_drawn", {"source": source, "target": target, "amount": amount})


class EnemyDeadEvent(Event):
    def __init__(self, source, target):
        super().__init__("enemy_dead", {"source": source, "target": target})


class EnemyDrawnEvent(Event):
    def __init__(self, enemy):
        super().__init__("enemy_drawn", {"enemy": enemy})


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


class CoinsDrawGivenEvent(Event):
    def __init__(self, source, target, amount):
        super().__init__("coins_draw", {"source": source, "target": target, "amount": amount})


class BoltsHealthGivenEvent(Event):
    def __init__(self, source, target, amount):
        super().__init__("bolts_health", {"source": source, "target": target, "amount": amount})


class ThrowDiceEvent(Event):
    def __init__(self, source, target, dice_type, amount, is_evil):
        super().__init__("throw_dice", {"source": source, "target": target, "dice_type": dice_type, "amount": amount, "is_evil": is_evil})


class CheckHandEvent(Event):
    def __init__(self, source, target):
        super().__init__("check_hand", {"source": source, "target": target})


class WeasleyEvent(Event):
    def __init__(self, source, target, effect_type, effect_amount, effect_target_type):
        super().__init__("weasley", {"source": source, "target": target, "effect_type": effect_type, "effect_amount": effect_amount, "effect_target_type": effect_target_type})
