import pprint
import random
import numpy as np


class Shape(object):
    NoShape = 0
    ZShape = 1
    SShape = 2
    LineShape = 3
    TShape = 4
    SquareShape = 5
    LShape = 6
    MirroredLShape = 7

    NAME = ["NoShape", "Z", "S", "Line", "T", "Square", "L", "ML"]
    SUB = [0, 2, 2, 2, 4, 1, 4, 4]

    MAX_SHAPE = 8
    MAX_SUB_SHAPE = 4
    MAX_POINT = 4
    MAX_WIDTH = 10

    SHAPE_TABLE = np.zeros((MAX_SHAPE, MAX_SUB_SHAPE, MAX_POINT, 2), np.int)
    SHAPE_TABLE[ZShape, 0] = ((0, 0), (0, 1), (1, 1), (1, 2))
    SHAPE_TABLE[ZShape, 1] = ((0, 1), (1, 1), (1, 0), (2, 0))

    SHAPE_TABLE[SShape, 0] = ((0, 2), (0, 1), (1, 1), (1, 0))
    SHAPE_TABLE[SShape, 1] = ((0, 0), (1, 0), (1, 1), (2, 1))

    SHAPE_TABLE[LineShape, 1] = ((1, 0), (1, 1), (1, 2), (1, 3))
    SHAPE_TABLE[LineShape, 0] = ((0, 1), (1, 1), (2, 1), (3, 1))

    SHAPE_TABLE[TShape, 0] = ((1, 0), (1, 1), (1, 2), (0, 1))
    SHAPE_TABLE[TShape, 1] = ((0, 1), (1, 1), (2, 1), (1, 2))
    SHAPE_TABLE[TShape, 2] = ((1, 0), (1, 1), (1, 2), (2, 1))
    SHAPE_TABLE[TShape, 3] = ((0, 1), (1, 1), (2, 1), (1, 0))

    SHAPE_TABLE[SquareShape, 0] = ((0, 0), (1, 0), (0, 1), (1, 1))

    SHAPE_TABLE[LShape, 0] = ((0, 1), (1, 1), (2, 1), (2, 2))
    SHAPE_TABLE[LShape, 1] = ((1, 0), (1, 1), (1, 2), (2, 0))
    SHAPE_TABLE[LShape, 2] = ((0, 1), (1, 1), (2, 1), (0, 0))
    SHAPE_TABLE[LShape, 3] = ((1, 0), (1, 1), (1, 2), (0, 2))

    SHAPE_TABLE[MirroredLShape, 0] = ((0, 1), (1, 1), (2, 1), (2, 0))
    SHAPE_TABLE[MirroredLShape, 1] = ((1, 0), (1, 1), (1, 2), (0, 0))
    SHAPE_TABLE[MirroredLShape, 2] = ((0, 1), (1, 1), (2, 1), (0, 2))
    SHAPE_TABLE[MirroredLShape, 3] = ((1, 0), (1, 1), (1, 2), (2, 2))

    SHAPE_WIDTH = []
    for p_shape in range(0, MAX_SHAPE):
        SHAPE_WIDTH.append([])
        for s_shape in range(SUB[p_shape]):
            max_x = np.max(SHAPE_TABLE[p_shape][s_shape][:, 1])
            min_x = np.min(SHAPE_TABLE[p_shape][s_shape][:, 1])
            SHAPE_WIDTH[p_shape].append(max_x - min_x + 1)

    ACTIONS = []
    for p_shape in range(0, MAX_SHAPE):
        ACTIONS.append([])
        for s_shape in range(SUB[p_shape]):
            ACTIONS[p_shape].append([i for i in range(MAX_WIDTH - SHAPE_WIDTH[p_shape][s_shape] + 1)])

    def __init__(self, p_shape=None):
        if p_shape is None:
            self.piece_shape = random.choice([self.SquareShape, self.LShape, self.MirroredLShape,
                                              self.TShape, self.LineShape, self.ZShape, self.SShape])
            self.piece_shape = self.SquareShape
        else:
            self.piece_shape = p_shape
        self.sub_shape = 0
        self.x = int(Shape.MAX_WIDTH/2-1)

    def set_x(self, x):
        if x < 0 or x > Shape.MAX_WIDTH - Shape.SHAPE_WIDTH[self.piece_shape][self.sub_shape]:
            # raise (Exception("Set X Error %d" % x))
            return
        self.x = x

    def move_left(self):
        self.set_x(self.x - 1)

    def move_right(self):
        self.set_x(self.x + 1)

    def set_shape(self, p_shape, s_shape=0):
        self.piece_shape = p_shape
        self.sub_shape = s_shape

    def set_sub_shape(self, s_shape):
        self.sub_shape = s_shape

    def get_shape(self):
        return self.piece_shape

    def get_name(self):
        return Shape.NAME[self.piece_shape]

    def get_pos(self):
        res = Shape.SHAPE_TABLE[self.piece_shape][self.sub_shape].copy()
        res[:, 1] -= np.min(res[:, 1])
        res[:, 1] += self.x
        return res

    def rotate_right(self, step=1):
        self.sub_shape += step
        self.sub_shape %= Shape.SUB[self.piece_shape]
        if self.x > Shape.MAX_WIDTH - Shape.SHAPE_WIDTH[self.piece_shape][self.sub_shape]:
            self.x = Shape.MAX_WIDTH - Shape.SHAPE_WIDTH[self.piece_shape][self.sub_shape]

    def rotate_left(self, step=1):
        self.sub_shape -= step
        self.sub_shape %= Shape.SUB[self.piece_shape]
        if self.x > Shape.MAX_WIDTH - Shape.SHAPE_WIDTH[self.piece_shape][self.sub_shape]:
            self.x = Shape.MAX_WIDTH - Shape.SHAPE_WIDTH[self.piece_shape][self.sub_shape]

    def get_actions(self):
        return Shape.ACTIONS[self.piece_shape]

    def print_shape(self):
        s_map = np.zeros((4, 4), np.int)
        for p in Shape.SHAPE_TABLE[self.piece_shape, self.sub_shape]:
            s_map[p[0], p[1]] = 1
        print("########", Shape.NAME[self.piece_shape], self.sub_shape, "########")
        pprint.pprint(s_map)
        # print('x:', self.x)
        # pprint.pprint(self.get_pos())
        print('Width', Shape.SHAPE_WIDTH[self.piece_shape][self.sub_shape])
        print('Actions:')
        pprint.pprint(Shape.ACTIONS[self.piece_shape])
        print()


if __name__ == '__main__':
    shape = Shape()
    for piece_shape in range(1, Shape.MAX_SHAPE):
        for sub_shape in range(Shape.SUB[piece_shape]):
            shape.set_shape(piece_shape, sub_shape)
            shape.print_shape()

    # for i in range(10):
    #     s1 = Shape()
    #     s1.print_shape()
    #
    # shape = Shape(Shape.LShape)
    # shape.print_shape()
    # shape.rotate_right(1)
    # shape.print_shape()
    # shape.rotate_right(1)
    # shape.print_shape()
    # shape.rotate_right(1)
    # shape.print_shape()
    # shape.rotate_right(1)
    # shape.print_shape()
    # shape.rotate_right(2)
    # shape.print_shape()
    # shape.rotate_left(2)
    # shape.print_shape()
    # shape.rotate_left(1)
    # shape.print_shape()
    # shape.rotate_left(1)
    # shape.print_shape()
    # shape.rotate_left(1)
    # shape.print_shape()
    # shape.rotate_left(1)
    # shape.print_shape()
    # shape.rotate_left(1)
    # shape.print_shape()
    # shape.rotate_left(1)
    # shape.print_shape()
    # shape.rotate_left(10)
    # shape.print_shape()
    # shape.set_shape(Shape.SquareShape)
    # shape.print_shape()
    # shape.rotate_left()
    # shape.print_shape()
    # shape.rotate_left()
    # shape.print_shape()
    # shape.rotate_left()
    # shape.print_shape()
    # shape.rotate_left()
    # shape.set_x(5)
    # shape.print_shape()
    # shape.set_x(8)
    # shape.print_shape()
    # shape.move_left()
    # shape.print_shape()
    # shape.move_left()
    # shape.print_shape()
    # shape.move_left()
    # shape.print_shape()


