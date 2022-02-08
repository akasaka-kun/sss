import random
import pygame
import tetrominos
import utilities
from config import screen, screen_bg, screen_size
from grid import Playfield
from tetrominos import Mino
from keyboard import Keyboard

pygame.init()

clk = pygame.time.Clock()
keyboard = Keyboard()

# setup testing field
field = Playfield()
field.grid[1, 1] = Mino('R', True)
i_timer = 0

done = False
while not done:

    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            done = True
        if e.type in (pygame.KEYUP, pygame.KEYDOWN):
            keyboard.add_event(e)
    keyboard.update()

    screen.fill(screen_bg)

    field.clear_lines()

    field_size = screen_size * 0.8
    field_size[0] = 0.5 * field_size[1]
    screen.blit(field.render(field_size), screen_size * 0.1)

    print(keyboard.actions)
    pygame.display.flip()

    clk.tick(60)
