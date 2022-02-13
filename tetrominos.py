import copy
import os.path
import numpy as np
import pygame.image
from numpy import array_equal

import utilities
from config import resources_path
from typing import Dict, Sequence, Tuple, List


class Color_set(dict):
    def __init__(self, kwargs):
        super(Color_set, self).__init__(kwargs)
        self.mino_texture = pygame.image.load(kwargs.get('__mino_texture', os.path.join(resources_path, 'textures/mino.png')))
        self.texture_dict = {}
        for i in kwargs:
            pass

    def texture_dict__repr__(self):
        return f'[<{"> <".join(f"{i[0]}:{self[i[0]]}, {i[1]}, {int(i[2])}" for i in self.texture_dict)}>]'

    def copy(self):
        copy_obj = Color_set({})
        for name, attr in self.__dict__.items():
            if hasattr(attr, 'copy') and callable(getattr(attr, 'copy')):
                copy_obj.__dict__[name] = attr.copy()
            else:
                copy_obj.__dict__[name] = copy.deepcopy(attr)
        return copy_obj

    def get_texture(self, color: str, size: Sequence, solid: bool):
        size = tuple(size)
        try:
            return self.texture_dict[(color, size, solid)]
        except KeyError:
            texture = pygame.transform.smoothscale(self.mino_texture, size).convert_alpha()
            if color == '0' and not solid:
                texture.fill('#00000000')
                self.texture_dict[(color, size, solid)] = texture
                return texture
            color_clip = pygame.Surface(size).convert_alpha()
            color_clip.fill('#' + ''.join(i * 2 for i in self[color]))
            texture.blit(color_clip, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
            if not solid:
                texture.set_alpha(128)
            self.texture_dict[(color, size, solid)] = texture
            return texture


class Mino:
    default_color_set = Color_set({'R': 'F33', 'G': '0F0', 'B': '00F', 'Y': 'FF0', 'O': 'F80', 'P': '80F', 'C': '0FF', '0': '888'})
    default_mino_texture = pygame.image.load(os.path.join(resources_path, 'textures/mino.png'))

    def __init__(self, color: str = '0', is_solid: bool = False, is_placed=False, color_set: dict = None, texture=default_mino_texture):
        if color_set is None: self.color_set = Mino.default_color_set
        if not isinstance(color, str) or not len(color) == 1: raise ValueError(f'color should be a 1 character long string', (color,))
        if color not in self.color_set: raise ValueError(f'Color {color} is not part of this Mino\'s color set')
        self.color = color
        self.solid = is_solid
        self.texture = texture
        self.placed = is_placed

    def __repr__(self):
        return f'{self.color}{int(self.solid) + int(self.placed)}'

    def render(self, size):
        return self.color_set.get_texture(self.color, size, self.solid)

    def place(self):
        self.placed = True
        self.solid = True
        return self

    def __eq__(self, other):
        if all([i == j for i, j in zip([self.color, self.solid, self.placed], [other.color, other.solid, other.placed])]):
            return True
        else:
            return False

    def copy(self):
        copy_obj = Mino()
        for name, attr in self.__dict__.items():
            if hasattr(attr, 'copy') and callable(getattr(attr, 'copy')):
                copy_obj.__dict__[name] = attr.copy()
            else:
                copy_obj.__dict__[name] = copy.deepcopy(attr)
        return copy_obj


class Rotation_system:
    class Rotation_table:

        def __init__(self, rotations: Dict[int, List[Tuple[int, int]]]):
            if len(rotations) != 4: raise ValueError('A rotation table must have exactly 4 orientation', (self,))
            self.rotations = rotations
            self.r0, self.r90, self.r180, self.r270 = self.rotations.values()

    class Kick_table:

        def __init__(self, kicks: Dict[Tuple[int, int], List[Tuple[int, int]]]):
            self.kicks = kicks

    def __init__(self, rotations: Dict[str, Rotation_table], kicks: Dict[str, Kick_table]):
        self.rotations = rotations
        self.kicks = kicks
        self.pieces = []


class Polymino:

    def __init__(self, pos: Sequence, rotation_table: Rotation_system.Rotation_table, kick_table: Rotation_system.Kick_table, color: str = '0', solid=True, placed=False):
        if len(pos) != 2: raise ValueError('pos needs to be a 2 item sequence')
        self.pos = np.array(pos)
        self.color = color
        self.solid = solid
        self.placed = placed
        self.angle = 0
        self.rotation_table = rotation_table
        self.kick_table = kick_table

    @property
    def absolute_minos(self):
        return self.rotation_table.rotations[self.angle % 360]

    @property
    def minos(self):
        return np.add(([self.pos] * len(self.rotation_table.rotations[self.angle % 360])), self.rotation_table.rotations[self.angle % 360])

    @property
    def Mino_type(self):
        return Mino(self.color, self.solid, self.placed)

    def place(self):
        self.placed = True

    def moved(self, movement):
        ret = copy.deepcopy(self)
        ret.pos += movement
        return ret

    def move(self, movement, field, ret=True):
        if field.is_legal(self.moved(movement), excepted=[elem for elem in self.minos if array_equal(elem, self.moved(movement).minos)]):
            self.pos += movement
        else:
            return None
        if ret: return self

    def kicked(self, kick):
        ret = copy.deepcopy(self)
        ret.pos += kick[0], -kick[1]  # todo this is a terrible workaround to the fact that the kick table is made for y up coordinates
        return ret

    def rotated(self, angle):
        ret = copy.deepcopy(self)
        if angle not in [90, -90, 180]: raise ValueError('can only rotate a polymino by 90, -90 or 180 degrees')
        ret.angle = (self.angle + angle) % 360
        return ret

    def rotate(self, angle, field, ret=True):
        try:
            for k in self.kick_table.kicks[(self.angle, (self.angle + angle) % 360)]:
                if not field.is_legal(self.rotated(angle).kicked(k)):
                    continue
                else:
                    utilities.become(self, self.rotated(angle).kicked(k))
                    break
        except KeyError:
            if field.is_legal(self.rotated(angle)):
                utilities.become(self, self.rotated(angle))
        if ret: return self


class Tetromino(Polymino):

    def __init__(self, pos: Sequence, rotation_table: Rotation_system.Rotation_table, kick_table: Rotation_system.Kick_table, color: str = '0'):
        super(Tetromino, self).__init__(pos, rotation_table, kick_table, color=color)
        if len(rotation_table.r0) != 4: raise ValueError('A tetromino must have exactly 4 minos', (rotation_table.r0,))
