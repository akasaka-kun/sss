import random
import pygame
import tetrominos
import utilities
from config import screen, screen_bg, screen_size
from grid import Playfield
from tetrominos import Mino

pygame.init()

clk = pygame.time.Clock()

# setup testing field
field = Playfield()
field.grid[1, 1] = Mino('R', True)
i_timer = 0

done = False
while not done:

    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            done = True

    screen.fill(screen_bg)

    # for testing
    i_timer += 1
    if i_timer > 20:
        if len([i for i in utilities.flatten(field.grid) if i != Mino()]) >= 40: field.clear()
        i_timer = 0
        yi_pos = random.randint(10, 18)
        i_pos = random.randint(0, 6)
        I = tetrominos.I((i_pos, yi_pos)).rotate(random.choice([90, -90, 180]), field)
        I.color = random.choice(list(Mino.default_color_set.keys()))
        if field.is_legal(I):
            print(I.minos)
            field.place_polymino(I)

    field.clear_lines()

    field_size = screen_size * 0.8
    field_size[0] = 0.5 * field_size[1]
    screen.blit(field.render(field_size), screen_size * 0.1)

    pygame.display.flip()

    clk.tick(60)
