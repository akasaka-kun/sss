import random
import re
import warnings

import pygame
import numpy as np
from copy import copy

import Controllers
import config
import ptext
from utilities import is_arr_in_list

import tetrominos
from tetrominos import Mino
from srs import srs


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

    def __init__(self, controller, type_=srs):
        self.grid_size = Playfield.DefaultSize
        self.grid = Mino_array(self.grid_size)

        self.type_ = type_
        self.queue = []
        self.controller: Controllers.Controller = controller

        # initialize fields
        self.SD_timer = None
        self.DAS_charge = None
        self.ARR_timer = None
        self.APT = None
        self.piece_floored = None
        self.gravity = None
        self.time = None
        self.gravity_timer = None

    # noinspection PyShadowingNames
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
                surf.blit((j if not is_arr_in_list((x, y), self.current_piece.minos) else Mino(self.current_piece.color, True)).render(np.array(size) / np.array(self.grid_size) + (GT / 2, GT / 2)), (x, y) * (np.array(size) / np.array(self.grid_size)) + (BT, BT))
                if config.debug.grid_index: ptext.draw(f'{x}, {y}', list(np.array([x, y]) * (np.array(size) / np.array(self.grid_size)) + (BT, BT)), surf=surf)  # debug
        return pygame.transform.smoothscale(surf, size / 2)

    def is_legal(self, polymino: tetrominos.Polymino, excepted=None):
        """
        :param excepted:
        :param polymino: any polymino
        :return: whether that polymino can be placed in a position without overriding any other mino
        """
        for m in polymino.minos:
            try:
                if self.grid[tuple(m)] != Mino() or any(n < 0 for n in m) and m not in excepted:
                    return False
            except IndexError:
                return False
            except TypeError:
                print(polymino.minos, polymino.pos, polymino.angle)
        return True

    def place_polymino(self, polymino: tetrominos.Polymino, solid=True, definitive=False, ret=False):
        """
        :param definitive:
        :param polymino: any polymino
        :param solid: whether to have it be solid or not. useful for preview shadow
        :param ret: what should this have returned again?
        """
        for m in polymino.minos:
            self.erase_mino(m, rep=Mino(polymino.color, solid, is_placed=definitive))

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

    def initialize(self):
        self.init_queue()
        self.init_new_piece()

        # to see if further need for initialization... SUCH AS ASSIGNING DIFFERENT CONTROLLERS

    def init_queue(self, empty=False, shuffle=True):
        self.queue = [piece(piece.spawn_pos) for piece in self.type_.pieces.copy()]
        if shuffle: random.shuffle(self.queue)

    def init_new_piece(self, pop=False):
        if pop: self.queue.pop(0)
        if len(self.queue) == 0:
            self.init_queue()
        self.time = 0
        self.gravity_timer = self.time
        self.gravity = config.gravity  # todo put in config
        self.APT = self.gravity  # todo if init new piece fails induce game over
        self.ARR_timer = 0
        self.SD_timer = 0
        self.DAS_charge = False

    def move_lr(self, direction, held):
        if not held[0]:
            self.current_piece.move(direction, self)
        if self.DAS_charge:
            if config.ARR == 0:
                while True:
                    moved = self.current_piece.move(direction, self)
                    if moved is None: break
            else:
                self.ARR_timer += 1
                if self.ARR_timer == config.ARR:
                    self.ARR_timer = 0
                    self.current_piece.move(direction, self)

    def drop_piece(self, type_):
        match type_:
            case 'soft':
                if np.isinf(config.SDF):
                    while True:
                        moved = self.current_piece.move((0, 1), self)
                        if moved is None: break
                else:
                    self.SD_timer += 1
                    if self.SD_timer == config.SDF:
                        self.SD_timer = 0
                        self.current_piece.move((0, 1), self)
            case 'hard':
                while True:
                    moved = self.current_piece.move((0, 1), self)
                    if moved is None: break
                self.place_polymino(self.current_piece, definitive=True)
                self.init_new_piece(pop=True)

    def update(self, place=False):
        self.time += 1
        self.gravity_timer += 1
        # gravity increase
        if self.time > config.gravity_inc_timer:
            self.gravity -= config.gravity_inc

        # control step
        # DAS charge
        if config.cancel_DAS_charge:
            for v in {k: v for k, v in self.controller.actions.items() if k in ('left', 'right')}.values():
                if v[0] and v[1] > config.DAS: self.DAS_charge = True
                else: self.DAS_charge = False
        else:
            if any([v[0] and v[1] > config.DAS for k, v in self.controller.actions.items() if k in ('left', 'right')]): self.DAS_charge = True
            else: self.DAS_charge = False
        # actual control
        for action, held in self.controller.actions.items():
            match action.split('_'):
                case ['left']:
                    self.move_lr((-1, 0), held)
                case ['right']:
                    self.move_lr((1, 0), held)
                case [type_, 'drop']:
                    match type_:
                        case 'soft':
                            self.drop_piece('soft')
                        case 'hard':
                            if not held[0]:
                                self.drop_piece('hard')
                case ['rotate', angle]:  # je crois avoir réussi?
                    if not held[0]:
                        self.current_piece.rotate({'cw': 90, 'ccw': -90, '180': 180}[angle], self)
                case ['hold']:  # todo ok either this one is the worst or it's ultra easy either way i need to add queue and hold to the renderer
                    pass

        # gravity step
        if self.gravity_timer >= self.gravity or self.piece_floored:
            if self.piece_floored:
                self.APT -= 1

            moved = self.current_piece.move((0, 1), self)
            if moved is None:
                self.piece_floored = True
            else:
                self.gravity_timer = 0
                self.piece_floored = False

        # soft placement
        if self.piece_floored and self.APT <= 0:
            # place piece down
            self.place_polymino(self.current_piece, solid=True, definitive=True)
            self.init_new_piece(pop=True)

    @property
    def current_piece(self):
        return self.queue[0]

    def __repr__(self):
        return repr(self.grid.transpose())


if __name__ == '__main__':
    pass
    # pf = Playfield()
    #
    # # for i, l in enumerate(pf.grid):
    # #     for j in range(len(l)):
    # #         color = random.choice(list(Mino.default_color_set.keys()))
    # #         pf.grid[i][j] = random.choice([Mino(), Mino(color, False), Mino(color, True)])
    #
    # z_pos = random.randint(0, 7)
    # yz_pos = 14
    # t = tetrominos.T((yz_pos, z_pos))
    # pf.place_polymino(t)
    #
    # for x in pf.grid:
    #     x[-4:] = Mino('0', True).place()
    # print(pf)
    #
    # pf.update()
    # print(pf)
    # pygame.image.save(pf.render((400, 800)), 'test.png')
