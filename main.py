import random
import typing
import pygame
import Controllers
import tetrominos
import utilities
from typing import List
from config import screen, screen_bg, screen_size
from grid import Playfield
from tetrominos import Mino
from Controllers import Keyboard

pygame.init()

clk = pygame.time.Clock()
keyboard1 = Keyboard()

# setup testing field
field = Playfield(keyboard1)
field.initialize()
field.update(place=True)

done = False
while not done:

    # event loop
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            done = True
    for Cs in Controllers.Controller.__subclasses__():
        for I in Cs.instances:
            I.update()

    # computing
    field.update()

    # rendering
    screen.fill(screen_bg)
    field_size = screen_size * 0.8
    field_size[0] = 0.5 * field_size[1]
    field.render(field_size, screen_size * 0.1)

    pygame.display.flip()

    clk.tick(60)
