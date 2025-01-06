import Effect


class EffectModifier:
    def modify(self, effect):
        return effect  # Default: no modification


class CantDrawCardsModifier(EffectModifier):
    def modify(self, effect):
        if isinstance(effect, Effect.DrawCardEffect):
            return None  # Prevent the effect
        return effect


class CantHealModifier(EffectModifier):
    def modify(self, effect):
        if isinstance(effect, Effect.HealEffect):
            return None
        return effect

