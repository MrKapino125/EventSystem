import Effect


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


class OneBoltPerEnemyModifier(EffectModifier):
    def __init__(self):
        self.bolts_placed_this_turn = {}

    def modify(self, effect, game_state, source, target):
        if not isinstance(effect, Effect.PlaceBoltEffect):
            return effect

        if target in self.bolts_placed_this_turn:
            print(f"Only one bolt can be placed on {target.name} this turn.")
            return None  # Prevent the effect
        else:
            self.bolts_placed_this_turn[target] = True
            return effect
