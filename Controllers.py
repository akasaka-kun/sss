import warnings
import pygame
import config


class Keyboard:
    instances = []

    def __init__(self):
        self.actions = {}
        self.events = []
        self.controls = config.keyboard_controls
        Keyboard.instances.append(self)

    def add_event(self, event):
        self.events.append(event)

    def update(self):
        for e in self.events:
            if e.key not in self.controls:
                continue
            match e.type:
                case pygame.KEYDOWN:
                    self.actions[self.controls[e.key]] = (True, self.actions.get(self.controls[e.key], (False, 0))[1] + 1)
                case pygame.KEYUP:
                    self.actions.pop(self.controls[e.key])
                case _:
                    warnings.warn(f"tried to feed {e} event into keyboard update method")