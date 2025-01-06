import Eventhandler
import Player
import State
import Effect
import EffectModifiers

event_handler = Eventhandler.EventHandler()
player1 = Player.Neville(None)
player2 = Player.Harry(None)
players = [player1, player2]
game_state = State.GameState(event_handler, players, 1)

#cant heal in this turn
#game_state.active_modifiers.append(EffectModifiers.CantHealModifier())
# Register the event handler
event_handler.register_listener("damage_taken", game_state.handle_damage_event)
event_handler.register_listener("health_gained", game_state.handle_heal_event)

# Dispatch a damage event
damage_effect = Effect.DamageEffect(9)
game_state.apply_effect(damage_effect, player1, [player2])

print(player2.health)

heal_effect = Effect.HealEffect(1)
game_state.apply_effect(heal_effect, player1, [player2])
print(player2.health)
game_state.apply_effect(heal_effect, player1, [player2])
print(player2.health)

#handle heal event for neville
#end turn event that triggers neville resetting his first heal given this turn