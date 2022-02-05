import random
import warnings
import pygame
import numpy as np
from copy import copy

import config
import ptext

import tetrominos
from tetrominos import Mino


def Mino_array(shape, mino=Mino()):
    a = np.empty(shape, dtype=Mino)
    a.fill(copy(mino))
    return a


class Playfield:
    DefaultSize = 10, 20
    border_color = (0, 0, 0, 255)
    border_width = 3 / 200
    gridlines_color = (64, 64, 64, 80)
    gridlines_thickness = 1 / 500

    def __init__(self):
        self.grid_size = Playfield.DefaultSize
        self.grid = Mino_array(self.grid_size)

    def render(self, size):
        size = np.array(size) * 2
        border_thickness = Playfield.border_width * size[1]
        BT = border_thickness
        gridlines_thickness = Playfield.gridlines_thickness * size[1]
        GT = gridlines_thickness
        full_size = np.array(size) + np.array((border_thickness * 2, border_thickness * 2))

        surf = pygame.Surface(full_size).convert_alpha()
        surf.fill((32, 32, 32, 255))

        pygame.draw.rect(surf, Playfield.border_color, (0, 0, *full_size), int(border_thickness))

        for x in range(self.grid_size[1] - 1):
            pygame.draw.line(surf, Playfield.gridlines_color, (BT, (x + 1) * (size[0] / self.grid_size[0]) + BT), (size[0] + BT, (x + 1) * (size[0] / self.grid_size[0]) + BT), int(gridlines_thickness))
        for y in range(self.grid_size[0] - 1):
            pygame.draw.line(surf, Playfield.gridlines_color, ((y + 1) * (size[1] / self.grid_size[1]) + BT, BT), ((y + 1) * (size[1] / self.grid_size[1]) + BT, size[1] + BT), int(gridlines_thickness))
        for x, l in enumerate(self.grid):
            for y, j in enumerate(l):
                surf.blit(j.render(np.array(size) / np.array(self.grid_size) + (GT / 2, GT / 2)), (x, y) * (np.array(size) / np.array(self.grid_size)) + (BT, BT))
                if config.debug.grid_index: ptext.draw(f'{x}, {y}', list(np.array([x, y]) * (np.array(size) / np.array(self.grid_size)) + (BT, BT)), surf=surf)  # debug

        return pygame.transform.smoothscale(surf, size / 2)

    def is_legal(self, polymino: tetrominos.Polymino):  # todo why are polymino still being wrapped round the grid x wise
        """
        :param polymino: any polymino
        :return: whether that polymino can be placed in a position without overriding any other mino
        """
        for m in polymino.minos:
            try:
                if self.grid[tuple(m)] != Mino():
                    return False
            except KeyError:
                return False
        return True

    def place_polymino(self, polymino: tetrominos.Polymino, solid=True, ret=False):
        """
        :param polymino: any polymino
        :param solid: whether to have it be solid or not. useful for preview shadow
        :param ret: what should this have returned again?
        """
        for m in polymino.minos:
            self.erase_mino(m, rep=Mino(polymino.color, solid))  # todo --fix the grid coordinate system-- ALMOST DONE, NOW FIX ALL THE REST

    def erase_mino(self, pos, rep=None):
        try:
            self.grid[tuple(pos)] = Mino() if rep is None else rep
        except IndexError:
            warnings.warn(f'tried to erase a mino outside of the field at pos {pos}')

    def clear(self):
        self.grid = Mino_array(self.grid_size)

    def clear_lines(self):
        for y, l in enumerate(self.grid.transpose()):
            if all(m.placed for m in l):
                self.grid = np.array([Mino_array(Playfield.DefaultSize[0]), *self.grid.transpose()[:y], *self.grid.transpose()[y + 1:]]).transpose()

    def __repr__(self):
        return repr(self.grid.transpose())


if __name__ == '__main__':
    pf = Playfield()

    # for i, l in enumerate(pf.grid):
    #     for j in range(len(l)):
    #         color = random.choice(list(Mino.default_color_set.keys()))
    #         pf.grid[i][j] = random.choice([Mino(), Mino(color, False), Mino(color, True)])

    z_pos = random.randint(0, 7)
    yz_pos = 14
    t = tetrominos.T((yz_pos, z_pos))
    pf.place_polymino(t)

    for x in pf.grid:
        x[-4:] = Mino('0', True).place()
    print(pf)

    pf.update()
    print(pf)
    pygame.image.save(pf.render((400, 800)), 'test.png')  # todo gameplay now
