import warnings
import pygame
import config


class Controller:

    def __init__(self, controls, instances):
        self.actions = {}
        self.events = []
        self.controls = controls
        instances.append(self)

    def add_event(self, event):
        self.events.append(event)


class Keyboard(Controller):
    instances = []

    def __init__(self):
        super(Keyboard, self).__init__(config.keyboard_controls, self.__class__.instances)

    def update(self):
        for e in self.events:
            if getattr(e, 'key', None) not in self.controls: continue
            match e.type:
                case pygame.KEYDOWN:
                    held = self.actions.get(self.controls[e.key], (False, 0))[1] + 1
                    self.actions[self.controls[e.key]] = (bool(self.actions.get(self.controls[e.key], False)), held)
                case pygame.KEYUP:
                    self.actions.pop(self.controls[e.key])
                    self.events = [ev for ev in self.events if ev.type not in (pygame.KEYDOWN, pygame.KEYUP) and getattr(e, 'key', None) != e.key]
