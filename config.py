import os.path
import numpy
import pygame

screen_size = numpy.array((800, 500))
screen_flags = 0
screen = pygame.display.set_mode(size=screen_size, flags=screen_flags)

resources_path = os.path.join(os.path.dirname(__file__), 'resources')

screen_bg = (32, 32, 32)

# these are for later
SDF = numpy.inf
ARR = 0
DAS = 7

keyboard_controls = {
    pygame.K_a: 'left',
    pygame.K_d: 'right',
    pygame.K_s: 'soft_drop',
    pygame.K_SPACE: 'hard_drop',
    pygame.K_LEFT: 'rotate_ccw',
    pygame.K_RIGHT: 'rotate_cw',
    pygame.K_DOWN: 'rotate_180'
}

class debug:
    grid_index = False
