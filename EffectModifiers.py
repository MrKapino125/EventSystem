import Effect
import Enemy
import Player


class EffectModifier:
    def modify(self, effect, game_state, source, targets):
        return effect  # Default: no modification


class CantDrawCardsModifier(EffectModifier):
    def modify(self, effect, game_state, source, targets):
        if isinstance(effect, Effect.DrawCardEffect):
            return None  # Prevent the effect
        return effect


class CantHealModifier(EffectModifier):
    def modify(self, effect, game_state, source, targets):
        if isinstance(effect, Effect.HealEffect):
            return None
        return effect


class CantPlaceSkullModifier(EffectModifier):
    def modify(self, effect, game_state, source, targets):
        if isinstance(effect, Effect.PlaceSkullEffect):
            return None
        return effect


class OneBoltPerEnemyModifier(EffectModifier):
    def __init__(self):
        self.bolts_placed_this_turn = {}

    def modify(self, effect, game_state, source, targets):
        target = targets[0]
        if not isinstance(effect, Effect.DamageEffect):
            return effect
        if not isinstance(target, Enemy.Enemy):
            return effect

        if target in self.bolts_placed_this_turn:
            return None  # Prevent the effect
        else:
            self.bolts_placed_this_turn[target] = True
            effect.amount = 1
            return effect


class BuyCardModifier(EffectModifier):
    def __init__(self, card_type):
        self.card_type = card_type


class EffectPerCardTypeModifier(EffectModifier):
    def __init__(self, effect, card_type, source, game_state):
        self.effect = effect
        self.card_type = card_type
        if source is not None:
            for card in source.cards_played:
                card_type = card.data["type"]
                if card_type == self.card_type:
                    game_state.apply_effect(self.effect, source, [source])

    def modify(self, effect, game_state, source, targets):
        if not isinstance(effect, Effect.CardPlayEffect):
            return effect

        if not isinstance(source, Player.Player):
            return effect

        card = effect.card
        card_type = card.data["type"]
        if card_type == self.card_type:
            game_state.apply_effect(self.effect, source, [source])
        return effect


class FirstEnemyKillModifier(EffectModifier):
    def __init__(self, effect, source, game_state):
        self.effect = effect
        self.deactivate = False
        for enemy in game_state.board.open_enemies:
            if enemy.is_dead:
                self.deactivate = True
                game_state.apply_effect(self.effect, source, [source])

    def modify(self, effect, game_state, source, targets):
        if not isinstance(effect, Effect.EnemyDeadEffect):
            return effect
        if not self.deactivate:
            self.deactivate = True
            game_state.apply_effect(self.effect, source, [source])
        return effect


class EffectPerFirstTypeModifier(EffectModifier):
    pass