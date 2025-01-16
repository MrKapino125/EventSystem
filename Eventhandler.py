import pygame
from sys import exit


class EventHandler:
    def __init__(self):
        self.listeners = {}
        self.mouse_pos = (0,0)
        self.is_clicked = {"left": False, "right": False, "middle": False}
        self.is_clicked_lock = self.is_clicked.copy()

    def tick(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            if event.type == pygame.MOUSEMOTION:
                self.mouse_pos = event.pos
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if self.is_clicked["left"]:
                        self.is_clicked_lock["left"] = True
                    self.is_clicked["left"] = True
                if event.button == 2:
                    if self.is_clicked["middle"]:
                        self.is_clicked_lock["middle"] = True
                    self.is_clicked["middle"] = True
                if event.button == 3:
                    if self.is_clicked["right"]:
                        self.is_clicked_lock["right"] = True
                    self.is_clicked["right"] = True
            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    self.is_clicked["left"] = False
                    self.is_clicked_lock["left"] = False
                if event.button == 2:
                    self.is_clicked["middle"] = False
                    self.is_clicked_lock["middle"] = False
                if event.button == 3:
                    self.is_clicked["right"] = False
                    self.is_clicked_lock["right"] = False

    def register_listener(self, event_type, listener):
        if event_type not in self.listeners:
            self.listeners[event_type] = []
            self.listeners[event_type].append(listener)

    def dispatch_event(self, event):
        if event.type in self.listeners:
            for listener in self.listeners[event.type]:
                listener(event)
