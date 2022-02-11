import warnings
import pygame
import config


class Controller:

    def __init__(self, controls, instances):
        self.actions = {}
        self.events = []
        self.controls = controls
        instances.append(self)


class Keyboard(Controller):
    instances = []

    def __init__(self):
        super(Keyboard, self).__init__(config.keyboard_controls, self.__class__.instances)

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
