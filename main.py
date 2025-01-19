import Eventhandler
import Player
import State
import Effect
import EffectModifiers
import Card
import sys
import pygame

pygame.init()

info = pygame.display.Info()
SCREEN_WIDTH = info.current_w
SCREEN_HEIGHT = info.current_h

SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption("Harry Potter: Kampf um Hogwarts!")

state_manager = State.StateManager()

event_handler = Eventhandler.EventHandler()
clock = pygame.time.Clock()

player1 = Player.Neville()
player2 = Player.Harry()
player3 = Player.Ron()
player4 = Player.Hermione()
players = [player1, player2, player3, player4]
players_keys = ["Neville Longbottom", "Harry Potter", "Ron Weasley", "Hermine Granger"]
game_state = State.GameState(event_handler, dict(zip(players_keys, players)), 1, state_manager, (SCREEN_WIDTH, SCREEN_HEIGHT))

#cant heal in this turn
#game_state.active_modifiers.append(EffectModifiers.CantHealModifier())
# Register the event handler
event_handler.register_listener("damage_taken", game_state.handle_damage_event)
event_handler.register_listener("health_gained", game_state.handle_heal_event)
event_handler.register_listener("bolt_given", game_state.handle_bolt_given_event)
event_handler.register_listener("bolt_placed", game_state.handle_bolt_placed_event)
event_handler.register_listener("coin_given", game_state.handle_coin_given_event)
event_handler.register_listener("card_played", game_state.handle_card_played_event)
event_handler.register_listener("card_drawn", game_state.handle_card_drawn_event)

# Dispatch a damage event


def tick():
    event_handler.tick()
    game_state.tick()


def render(screen):
    screen.fill((200, 200, 200))  # Light gray background
    game_state.render(screen)
    pygame.display.flip()


while True:
    clicked = False

    tick()
    render(SCREEN)

    clock.tick(60)
