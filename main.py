import Eventhandler
import Player
import State
import Effect
import EffectModifiers
import Card
import sys
import pygame
import ctypes

# DPI-Awareness setzen (VOR pygame.init() und pygame.display.set_mode())
if hasattr(ctypes.windll.user32, 'SetProcessDPIAware'):
    ctypes.windll.user32.SetProcessDPIAware()

pygame.init()

info = pygame.display.Info()
SCREEN_WIDTH = info.current_w
SCREEN_HEIGHT = info.current_h

SCREEN = pygame.display.set_mode((0,0), pygame.FULLSCREEN)
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
