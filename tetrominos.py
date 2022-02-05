import copy
import os.path
import numpy as np
import pygame.image

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
            print(self.texture_dict__repr__())
            return texture


class Mino:
    default_color_set = Color_set({'R': 'F33', 'G': '0F0', 'B': '00F', 'Y': 'FF0', 'O': 'F80', 'P': '80F', 'C': '0FF', '0': '888'})
    default_mino_texture = pygame.image.load(os.path.join(resources_path, 'textures/mino.png'))

    def __init__(self, color: str = '0', is_solid: bool = False, color_set: dict = None, texture=default_mino_texture):
        if color_set is None: self.color_set = Mino.default_color_set
        if not isinstance(color, str) or not len(color) == 1: raise ValueError(f'color should be a 1 character long string', (color,))
        if color not in self.color_set: raise ValueError(f'Color {color} is not part of this Mino\'s color set')
        self.color = color
        self.solid = is_solid
        self.texture = texture
        self.placed = False

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


class Polymino:

    def __init__(self, pos: Sequence, rotation_table: Rotation_system.Rotation_table, kick_table: Rotation_system.Kick_table, color: str = '0'):
        if len(pos) != 2: raise ValueError('pos needs to be a 2 item sequence')
        self.pos = np.array(pos)
        self.color = color
        self.minos = np.add(([pos] * len(rotation_table.r0)), rotation_table.r0)
        self.angle = 0
        self.rotation_table = rotation_table
        self.kick_table = kick_table

    def is_clipping(self, field, kick=None):
        if kick is None: kick = [0, 0]
        oob_clip = True
        try:
            if any(field.grid[tuple(self.pos + np.array(m) + kick)] != Mino() for m in self.minos):
                oob_clip = False
                raise IndexError
            else:
                return False
        except IndexError:
            return True, oob_clip

    def _kicked(self, kick):
        ret = copy.deepcopy(self)
        ret.pos += kick
        return ret

    def _rotated(self, angle):
        ret = copy.deepcopy(self)
        if angle not in [90, -90, 180]: raise ValueError('can only rotate a polymino by 90, -90 or 180 degrees')
        ret.angle = self.angle + angle
        ret.minos = np.add(([ret.pos] * len(self.rotation_table.rotations[ret.angle])), ret.rotation_table.r0)
        return ret

    def rotate(self, angle, field, ret=True):
        for k in self.kick_table.kicks[(self.angle, (self.angle + angle) % 360)]:
            if not field.is_legal(self._rotated(angle)._kicked(k)):
                continue
            else:
                utilities.become(self, self._rotated(angle)._kicked(k))
        if ret: return self


class Tetromino(Polymino):

    def __init__(self, pos: Sequence, rotation_table: Rotation_system.Rotation_table, kick_table: Rotation_system.Kick_table, color: str = '0'):
        super(Tetromino, self).__init__(pos, rotation_table, kick_table, color=color)
        if len(rotation_table.r0) != 4: raise ValueError('A tetromino must have exactly 4 minos', (rotation_table.r0,))


# noinspection SpellCheckingInspection

srs = Rotation_system(
    {
        'T': Rotation_system.Rotation_table({
            0: [(0, 1), (1, 1), (2, 1), (1, 0)],
            90: [(1, 2), (1, 1), (2, 1), (1, 0)],
            180: [(0, 1), (1, 1), (2, 1), (1, 2)],
            270: [(1, 0), (1, 1), (0, 1), (1, 2)]
        }),
        'S': Rotation_system.Rotation_table({
            0: [(1, 0), (2, 0), (0, 1), (1, 1)],
            90: [(1, 0), (1, 1), (2, 1), (2, 2)],
            180: [(1, 1), (2, 1), (0, 2), (1, 2)],
            270: [(0, 0), (0, 1), (1, 1), (1, 2)]
        }),
        'Z': Rotation_system.Rotation_table({
            0: [(0, 0), (1, 0), (1, 1), (2, 1)],
            90: [(2, 0), (1, 1), (2, 1), (1, 2)],
            180: [(1, 1), (0, 1), (2, 2), (1, 2)],
            270: [(1, 0), (0, 1), (1, 1), (0, 2)]
        }),
        'J': Rotation_system.Rotation_table({
            0: [(0, 0), (0, 1), (1, 1), (2, 1)],
            90: [(2, 0), (1, 0), (1, 1), (1, 2)],
            180: [(2, 2), (0, 1), (1, 1), (2, 1)],
            270: [(0, 2), (1, 0), (1, 1), (1, 2)]
        }),
        'L': Rotation_system.Rotation_table({
            0: [(2, 0), (0, 1), (1, 1), (2, 1)],
            90: [(2, 2), (1, 0), (1, 1), (1, 2)],
            180: [(0, 2), (0, 1), (1, 1), (2, 1)],
            270: [(0, 0), (1, 0), (1, 1), (1, 2)]
        }),
        'O': Rotation_system.Rotation_table({
            0: (O_r0 := [(0, 0), (0, 1), (1, 1), (1, 0)]),
            90: O_r0,
            180: O_r0,
            270: O_r0
        }),
        'I': Rotation_system.Rotation_table({
            0: [(0, 1), (1, 1), (2, 1), (3, 1)],
            90: [(2, 0), (2, 1), (2, 2), (2, 3)],
            180: [(0, 2), (1, 2), (2, 2), (3, 2)],
            270: [(1, 0), (1, 1), (1, 2), (1, 3)]
        })},
    {
        'T': (srs_tszlj_kicks := Rotation_system.Kick_table({
            (0, 90): [(0, 0), (-1, 0), (-1, 1), (0, -2), (-1, -2)],
            (90, 0): [(0, 0), (1, 0), (1, -1), (0, 2), (1, 2)],
            (90, 180): [(0, 0), (1, 0), (1, -1), (0, 2), (1, 2)],
            (180, 90): [(0, 0), (-1, 0), (-1, 1), (0, -2), (-1, -2)],
            (180, 270): [(0, 0), (1, 0), (1, 1), (0, -2), (1, -2)],
            (270, 180): [(0, 0), (-1, 0), (-1, -1), (0, 2), (-1, 2)],
            (270, 0): [(0, 0), (-1, 0), (-1, -1), (0, 2), (-1, 2)],
            (0, 270): [(0, 0), (1, 0), (1, 1), (0, -2), (1, -2)],
            # 180s
            (0, 180): [(0, 0), (0, 1), (1, 1), (-1, 1), (1, 0), (-1, 0)],
            (180, 0): [(0, 0), (0, -1), (-1, -1), (1, -1), (-1, 0), (1, 0)],
            (90, 270): [(0, 0), (1, 0), (1, 2), (1, 1), (0, 2), (0, 1)],
            (270, 90): [(0, 0), (-1, 0), (-1, 2), (-1, 1), (0, 2), (0, 1)]
        })),
        'S': srs_tszlj_kicks,
        'Z': srs_tszlj_kicks,
        'J': srs_tszlj_kicks,
        'L': srs_tszlj_kicks,
        'I': Rotation_system.Kick_table({
            (0, 90): [(1, 0), (-2, 0), (-2, 1), (1, -2)],
            (90, 0): [(-1, 0), (2, 0), (-1, 2), (2, -1)],
            (90, 180): [(-1, 0), (2, 0), (-1, -2), (2, 1)],
            (180, 90): [(-2, 0), (1, 0), (-2, -1), (1, 2)],
            (180, 270): [(2, 0), (-1, 0), (2, -1), (-1, 2)],
            (270, 180): [(1, 0), (-2, 0), (1, -2), (-2, 1)],
            (270, 0): [(1, 0), (-2, 0), (1, 2), (-2, -1)],
            (0, 270): [(-1, 0), (2, 0), (2, 1), (-1, -2)],
            # 180s
            (0, 180): [(0, -1)], (90, 270): [(1, 0)], (180, 0): [(0, 1)], (270, 90): [(-1, 0)]
        }),
        # O literally can't rotate into a kick situation
        'O': Rotation_system.Kick_table({})})


class T(Tetromino):  # todo start making gameplay

    def __init__(self, pos: Sequence, rotation_system: Rotation_system = srs):
        super(T, self).__init__(pos, rotation_system.rotations['T'], rotation_system.kicks['T'], color='P')


class S(Tetromino):

    def __init__(self, pos: Sequence, rotation_system: Rotation_system = srs):
        super(S, self).__init__(pos, rotation_system.rotations['S'], rotation_system.kicks['S'], color='G')


class Z(Tetromino):

    def __init__(self, pos: Sequence, rotation_system: Rotation_system = srs):
        super(Z, self).__init__(pos, rotation_system.rotations['Z'], rotation_system.kicks['Z'], color='R')


class J(Tetromino):

    def __init__(self, pos: Sequence, rotation_system: Rotation_system = srs):
        super(J, self).__init__(pos, rotation_system.rotations['J'], rotation_system.kicks['J'], color='B')


class L(Tetromino):

    def __init__(self, pos: Sequence, rotation_system: Rotation_system = srs):
        super(L, self).__init__(pos, rotation_system.rotations['L'], rotation_system.kicks['L'], color='O')


class I(Tetromino):

    def __init__(self, pos: Sequence, rotation_system: Rotation_system = srs):
        super(I, self).__init__(pos, rotation_system.rotations['I'], rotation_system.kicks['I'], color='C')


if __name__ == '__main__':
    Tetromino([0, 0], srs.rotations['T'], srs.kicks['T'])
