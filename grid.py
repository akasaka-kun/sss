import os.path
import random
import re
import sys
import warnings

import pygame
import numpy as np
from copy import copy, deepcopy

import Controllers
import config
import ptext
from utilities import is_arr_in_list

import tetrominos
from tetrominos import Mino
from srs import srs


class Playfield:
    RenderedGridSize = 10, 20
    FieldSize = [0, 10], [-2, 20]
    border_color = (0, 0, 0, 255)
    border_width = 3 / 200
    gridlines_color = (64, 64, 64, 80)
    gridlines_thickness = 1 / 500
    queue_texture = pygame.image.load(os.path.join(config.resources_path, 'textures/queue.png'))

    def __init__(self, controller, type_=srs):
        self.grid_size = Playfield.RenderedGridSize
        self.minos = {}

        self.type_ = type_
        self.queue = []
        self.next_queue = []
        self.controller: Controllers.Controller = controller

        # settings :
        self.special_moves = {}  # todo implement special moves detection

        # initialize fields
        self.has_switched = None
        self.held_piece = None
        self.SD_timer = None
        self.DAS_charge = None
        self.ARR_timer = None
        self.APT = None
        self.piece_floored = None
        self.gravity = None
        self.time = None
        self.gravity_timer = None

    # noinspection PyShadowingNames,SpellCheckingInspection
    def render(self, size_, field_pos):
        PFsize = np.array(size_) * 2
        border_thickness = Playfield.border_width * PFsize[1]
        BT = border_thickness
        gridlines_thickness = Playfield.gridlines_thickness * PFsize[1]
        GT = gridlines_thickness
        queue_size = PFsize[0] * 0.3
        field_size = np.array(PFsize) + np.array((border_thickness * 2, border_thickness * 2))
        full_size = field_size + np.array([queue_size, 0])

        surf = pygame.Surface(full_size).convert_alpha()
        surf.fill((*config.screen_bg, 255))

        # draw playfield
        pygame.draw.rect(surf, Playfield.border_color, (0, 0, *field_size), int(border_thickness))
        # draw queue
        surf.blit(pygame.transform.smoothscale(Playfield.queue_texture, (queue_size, queue_size * 6)), (full_size[0] - queue_size, 0))
        for y, piece in enumerate([self.held_piece, *self.queue[1:], *self.next_queue][:6]):
            if piece is None: continue
            piece: tetrominos.Polymino
            piece_size = max(m[0] for m in piece.absolute_minos), max(m[1] for m in piece.absolute_minos)
            render_grid = piece_size + np.array([3, 3])
            render_grid = np.array([max(render_grid)] * 2)
            for i in piece.absolute_minos:
                surf.blit(Mino(piece.color, True).render([queue_size] * 2 / render_grid),
                          (field_size[0] + ((queue_size / render_grid[0]) * (i[0] + 1)), (queue_size * y) + ((queue_size / render_grid[1]) * (i[1] + 1))))

        for x in range(self.grid_size[1] - 1):
            pygame.draw.line(surf, Playfield.gridlines_color, (BT, (x + 1) * (PFsize[0] / self.grid_size[0]) + BT), (PFsize[0] + BT, (x + 1) * (PFsize[0] / self.grid_size[0]) + BT), int(gridlines_thickness))
        for y in range(self.grid_size[0] - 1):
            pygame.draw.line(surf, Playfield.gridlines_color, ((y + 1) * (PFsize[1] / self.grid_size[1]) + BT, BT), ((y + 1) * (PFsize[1] / self.grid_size[1]) + BT, PFsize[1] + BT), int(gridlines_thickness))
        if config.debug.grid_index:
            for x in range(self.grid_size[0]):
                for y in range(self.grid_size[1]):
                    ptext.draw(f'{x}, {y}', list([x, y] * (np.array(PFsize) / np.array(self.grid_size)) + np.array((BT, BT))), surf=surf)

        pygame.display.get_surface().blit(pygame.transform.smoothscale(surf, full_size / 2), field_pos)

        for pos, mino in {**self.minos, **{k: v for k, v in zip([tuple(m) for m in self.current_piece.minos], [self.current_piece.Mino_type] * len(self.current_piece.minos))}}.items():
            relative_pos_to_field = (pos + np.array((2, 1))) * (np.array(PFsize) / np.array(self.grid_size)) + (0, BT)  # todo find the true reason i need to add this hardcoded offset + (0, BT)
            mino_size = np.array(PFsize) / np.array(self.grid_size) + (GT / 2, GT / 2)
            pygame.display.get_surface().blit(mino.render(mino_size // 2), (field_pos + (BT, BT) + relative_pos_to_field) // 2)

    def is_legal(self, polymino: tetrominos.Polymino, excepted=None):
        """
        :param excepted:
        :param polymino: any polymino
        :return: whether that polymino can be placed in a position without overriding any other mino
        """
        if excepted is None: excepted = []
        for m in polymino.minos:
            try:
                if self.get_mino(m) != Mino() or \
                        not (self.FieldSize[0][0] <= m[0] < self.FieldSize[0][1] and self.FieldSize[1][0] <= m[1] < self.FieldSize[1][1]) \
                        and m not in excepted:
                    return False
            except IndexError:
                return False
        return True

    def get_mino(self, pos, default=None, minos=None):
        return (self.minos if minos is None else minos).get(tuple(pos), Mino() if default is None else default)

    def del_mino(self, pos, rep=None, minos=None):
        if rep is None:
            (self.minos if minos is None else minos).pop(tuple(pos))
        else:
            (self.minos if minos is None else minos)[tuple(pos)] = rep

    def set_mino(self, pos, mino, minos=None):
        (self.minos if minos is None else minos)[tuple(pos)] = mino

    def place_polymino(self, polymino: tetrominos.Polymino, solid=True, definitive=False, ret=False):
        """
        :param definitive:
        :param polymino: any polymino
        :param solid: whether to have it be solid or not. useful for preview shadow
        :param ret: what should this have returned again?
        """

        for m in polymino.minos:
            self.del_mino(m, rep=Mino(polymino.color, solid, is_placed=definitive))
        cleared_lines = 0
        for m in polymino.minos:
            cleared_lines += 1 if self.clear_line(m[1]) is True else 0
        if cleared_lines: print('cleared', cleared_lines, 'lines')

    def clear_line(self, y, no_check=False):
        new_minos = {}
        if sorted([i[0] for i, m in self.minos.items() if i[1] == y and m.solid]) == list(range(*(Playfield.FieldSize[0]))):
            for i, m in self.minos.items():
                if m.placed and m.solid:
                    if i[1] > y:
                        self.set_mino(i, m, minos=new_minos)
                    elif i[1] < y:
                        self.set_mino(i + np.array([0, 1]), m, minos=new_minos)
            self.minos.clear()
            self.minos.update(new_minos)
            return True

    def initialize(self):
        self.init_new_piece()
        # todo see if further need for initialization... SUCH AS ASSIGNING DIFFERENT CONTROLLERS

    def new_bag(self, empty=False, shuffle=True, bag=None):
        bag = [piece(piece.spawn_pos) for piece in self.type_.pieces.copy()] if bag is None else bag
        if shuffle: random.shuffle(bag)
        if empty: self.queue.clear()
        self.queue += bag

    def init_new_piece(self, pop=False):
        if pop: ret = self.queue.pop(0)
        while len(self.queue) < 7:
            self.new_bag()
        self.time = 0
        self.gravity_timer = self.time
        self.gravity = config.gravity
        self.APT = self.gravity  # todo if init new piece fails induce game over
        self.ARR_timer = 0
        self.SD_timer = 0
        self.DAS_charge = False
        self.has_switched = False
        if pop:  # noinspection PyUnboundLocalVariable
            return ret

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
                if v[0] and v[1] > config.DAS:
                    self.DAS_charge = True
                else:
                    self.DAS_charge = False
        else:
            if any([v[0] and v[1] > config.DAS for k, v in self.controller.actions.items() if k in ('left', 'right')]):
                self.DAS_charge = True
            else:
                self.DAS_charge = False
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
                case ['rotate', angle]:
                    if not held[0]:
                        self.current_piece.rotate({'cw': 90, 'ccw': -90, '180': 180}[angle], self)
                case ['hold']:
                    if not held[0] and not self.has_switched:
                        if self.held_piece:
                            transfer: tetrominos.Polymino = self.held_piece
                            transfer = transfer.__class__(transfer.__class__.spawn_pos)
                            # transfer = self.type_.pieces.copy()
                            self.queue.insert(0, transfer)
                            self.init_new_piece()
                            self.held_piece = self.queue.pop(1)
                            self.held_piece = self.held_piece.__class__(transfer.__class__.spawn_pos)
                        else:
                            self.held_piece = self.init_new_piece(pop=True)
                        self.has_switched = True

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
    def current_piece(self) -> tetrominos.Polymino:
        return self.queue[0]

    def __repr__(self):  # todo this is broke
        return repr(self.minos)


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
