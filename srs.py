from tetrominos import Rotation_system, Tetromino
from typing import Sequence

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


class T(Tetromino):

    def __init__(self, pos: Sequence, rotation_system: Rotation_system = srs):
        super(T, self).__init__(pos, rotation_system.rotations['T'], rotation_system.kicks['T'], color='P')
    spawn_pos = 4, 0


class S(Tetromino):

    def __init__(self, pos: Sequence, rotation_system: Rotation_system = srs):
        super(S, self).__init__(pos, rotation_system.rotations['S'], rotation_system.kicks['S'], color='G')
    spawn_pos = 4, 0


class Z(Tetromino):

    def __init__(self, pos: Sequence, rotation_system: Rotation_system = srs):
        super(Z, self).__init__(pos, rotation_system.rotations['Z'], rotation_system.kicks['Z'], color='R')
    spawn_pos = 4, 0


class J(Tetromino):

    def __init__(self, pos: Sequence, rotation_system: Rotation_system = srs):
        super(J, self).__init__(pos, rotation_system.rotations['J'], rotation_system.kicks['J'], color='B')
    spawn_pos = 4, 0


class L(Tetromino):

    def __init__(self, pos: Sequence, rotation_system: Rotation_system = srs):
        super(L, self).__init__(pos, rotation_system.rotations['L'], rotation_system.kicks['L'], color='O')
    spawn_pos = 4, 0


class I(Tetromino):

    def __init__(self, pos: Sequence, rotation_system: Rotation_system = srs):
        super(I, self).__init__(pos, rotation_system.rotations['I'], rotation_system.kicks['I'], color='C')
    spawn_pos = 3, 0


class O(Tetromino):

    def __init__(self, pos: Sequence, rotation_system: Rotation_system = srs):
        super(O, self).__init__(pos, rotation_system.rotations['O'], rotation_system.kicks['O'], color='Y')
    spawn_pos = 4, 0


srs.pieces = [T, S, Z, L, J, O, I]



