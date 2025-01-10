import Eventhandler
import Player
import State
import Effect
import EffectModifiers
import Card

event_handler = Eventhandler.EventHandler()
player1 = Player.Neville(None)
player2 = Player.Harry(None)
players = [player1, player2]
game_state = State.GameState(event_handler, players, 7)

#cant heal in this turn
game_state.active_modifiers.append(EffectModifiers.CantHealModifier())
# Register the event handler
event_handler.register_listener("damage_taken", game_state.handle_damage_event)
event_handler.register_listener("health_gained", game_state.handle_heal_event)
event_handler.register_listener("bolt_given", game_state.handle_bolt_given_event)
event_handler.register_listener("bolt_placed", game_state.handle_bolt_placed_event)
event_handler.register_listener("coin_given", game_state.handle_coin_given_event)
event_handler.register_listener("card_played", game_state.handle_card_played_event)

# Dispatch a damage event
cards = Card.load_cards(1)
game_state.apply_effect(Effect.DamageEffect(5), None, [player1, player2])

print(player1.health)
print(player1.bolts)

cards[2].play(player1, game_state)

print(player1.health)
print(player1.bolts)


