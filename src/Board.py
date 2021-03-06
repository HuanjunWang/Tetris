import pprint

import numpy as np

from LinearQLearning import QLearnPlayer
from Shape import Shape


class Board(object):
    BOARD_WIDTH = Shape.MAX_WIDTH
    BOARD_HEIGHT = 20
    GAME_OVER_HEIGHT = 16

    def __init__(self):
        self.with_gui = False
        self.total_removed_lines = 0
        self.average = 0
        self.round = 0
        self.INFO_ROUND = 1000
        self.max_removed = 0
        self.debug = False

        self.cur_shape = None
        self.cur_y = None
        self.bad_pos = None
        self.last_bad_pos = None
        self.var = None
        self.last_var = None
        self.BOARD_M_FULL = self.get_full_board_m()

        self.board = None
        self.board_m = None

        self.num_of_full_lines = None
        self.cur_removed_lines = None
        self.one_removed_lines = None
        self.started = None
        self.init()

        self.__total_points = 0
        self.__removed_points = 0

    def set_mode(self, gui, debug):
        self.with_gui = gui
        self.debug = debug

    def init(self):
        self.board = np.zeros((Board.BOARD_HEIGHT, Board.BOARD_WIDTH), np.int)
        self.board_m = np.zeros((Board.BOARD_HEIGHT + 1, Board.BOARD_WIDTH), np.int)
        # self.total_removed_lines = 0
        self.cur_removed_lines = 0
        self.one_removed_lines = 0
        self.started = True
        self.round += 1
        self.bad_pos = 0
        self.last_bad_pos = 0
        self.var = 0
        self.last_var = 0
        self.cur_shape = None
        self.num_of_full_lines = 0
        self.__removed_points = 0
        self.__total_points = 0

    def next_step(self, fast=False):
        '''
            If cur_shape exit, move down one step
            If fast set, move to bottom
            return false when game_over, remove true otherwise
        '''
        if self.num_of_full_lines:
            self.remove_full_lines()
            self.num_of_full_lines = 0
            return True

        if not self.cur_shape:
            self.new_shape()
            # raise Exception("cur_shape is None")
            return True

        if fast:
            return self.add_shape_without_remove(self.cur_shape)
        else:
            return self.move_down(1)

    def get_min_distance(self):
        pos = self.cur_shape.get_pos()
        cur_h = np.argmax(self.board_m, axis=0)
        min_distance = Board.BOARD_HEIGHT
        for y, x in pos:
            if (self.cur_y - y - cur_h[x]) < min_distance:
                min_distance = self.cur_y - y - cur_h[x]
        return min_distance

    def move_down(self, lines):
        self.cur_y -= lines
        res = True
        if self.get_min_distance() <= 0 or lines == 0:
            res = self.add_shape(self.cur_shape)
            self.cur_shape = None
        return res

    def move_left(self):
        if not self.cur_shape:
            return
        self.cur_shape.move_left()

    def move_right(self):
        if not self.cur_shape:
            return
        self.cur_shape.move_right()

    def rotate_left(self):
        if not self.cur_shape:
            return
        self.cur_shape.rotate_left()

    def rotate_right(self):
        if not self.cur_shape:
            return
        self.cur_shape.rotate_right()

    def new_shape(self, shape=None):
        self.cur_y = Board.BOARD_HEIGHT - 1
        self.cur_shape = Shape(shape)
        return self.cur_shape

    def get_reward(self):
        # print(self.last_bad_pos, self.bad_pos, self.last_var, self.var, self.one_removed_lines)
        reward = (self.last_bad_pos - self.bad_pos) * 7
        # print(reward)
        reward += self.one_removed_lines * 4
        # print(reward)
        reward += self.last_var - self.var
        # print(reward)
        self.one_removed_lines = 0
        return reward

    def start_training(self):
        player = QLearnPlayer()
        player.set_features(Board.BOARD_WIDTH * (Board.GAME_OVER_HEIGHT + 1),
                            [Shape.MAX_SHAPE, max(Shape.SUB), Board.BOARD_WIDTH])
        player.set_debug(player.DEBUG_LEVEL0, True)
        player.load_theta('theta_53_15.034')

        while True:
            self.init()
            while self.started:
                new_shape = self.new_shape()

                action = player.select_action(self.get_feature_vector(), new_shape)
                new_shape.set_sub_shape(action[0])
                new_shape.set_x(action[1])

                self.add_shape(new_shape)
                if self.debug:
                    self.print_info()

                if self.cur_removed_lines > 1000:
                    print("theta_%d_%.3f" % (self.cur_removed_lines, self.average))
                    player.save_theta("theta_%d_%.3f" % (self.max_removed, self.average))
                    return

                if self.started:
                    player.update(self.get_feature_vector(), self.get_reward(), self.new_shape())
                else:
                    self.point_check()
                    player.update(np.zeros(self.BOARD_WIDTH * (self.GAME_OVER_HEIGHT + 1)), -3,
                                  new_shape)

            if self.round % self.INFO_ROUND == 0:
                self.average = self.total_removed_lines / self.INFO_ROUND
                # self.print_info()
                print("Round: %-10d" % self.round, "Max:", self.max_removed, "Avg:", self.average)
                self.total_removed_lines = 0

                if self.round % (self.INFO_ROUND * 10) == 0:
                    player.save_theta("theta_%d_%.3f" % (self.max_removed, self.average))

                self.max_removed = 0

    @staticmethod
    def get_full_board_m():
        res = np.zeros((Board.BOARD_HEIGHT + 1, Board.BOARD_WIDTH), np.int)
        for i in range(Board.BOARD_HEIGHT + 1):
            res[i] = i
        return res

    # x start from 0 and y start from 0
    def set_pos(self, x, y, v):
        self.board[y, x] = v
        self.board_m[y + 1, x] = y + 1

    def get_feature_vector(self):
        res = np.zeros(self.BOARD_WIDTH * (self.GAME_OVER_HEIGHT + 1))
        top = np.argmax(self.board_m, axis=0)
        top -= min(top)

        for i in range(top.shape[0]):
            res[i * (self.GAME_OVER_HEIGHT + 1) + top[i]] = 1

        return res

    def point_check(self):
        cur_num = np.sum(self.board > 0)
        if cur_num != (self.__total_points - self.__removed_points):
            raise Exception("Point Check Error")

    def add_shape(self, n_shape=None):

        self.__total_points += Shape.MAX_POINT

        if n_shape is None:
            n_shape = self.cur_shape

        pos = n_shape.get_pos()
        cur_h = np.argmax(self.board_m, axis=0)

        min_distance = Board.BOARD_HEIGHT
        for y, x in pos:
            if (self.cur_y - y - cur_h[x]) < min_distance:
                min_distance = self.cur_y - y - cur_h[x]

        for y, x in pos:
            self.set_pos(x, self.cur_y - y - min_distance, n_shape.get_shape())

        self.remove_full_lines()
        self.cur_shape = None

        if np.max(self.board_m) > Board.GAME_OVER_HEIGHT:
            self.started = False
            self.total_removed_lines += self.cur_removed_lines
            if self.cur_removed_lines > self.max_removed:
                self.max_removed = self.cur_removed_lines
                # print("#########GAME OVER#########")
            return False

        self.calculate()
        return True

    def add_shape_without_remove(self, n_shape=None):
        self.__total_points += Shape.MAX_POINT
        if n_shape is None:
            n_shape = self.cur_shape
        pos = n_shape.get_pos()
        cur_h = np.argmax(self.board_m, axis=0)

        min_distance = Board.BOARD_HEIGHT
        for y, x in pos:
            if (self.cur_y - y - cur_h[x]) < min_distance:
                min_distance = self.cur_y - y - cur_h[x]

        for y, x in pos:
            self.set_pos(x, self.cur_y - y - min_distance, n_shape.get_shape())

        # self.remove_full_lines()
        to_remove = np.nonzero(np.all(self.board, axis=1))[0]
        self.num_of_full_lines = len(to_remove)

        self.cur_shape = None

        if np.max(self.board_m) > Board.GAME_OVER_HEIGHT:
            self.started = False
            self.total_removed_lines += self.cur_removed_lines
            if self.cur_removed_lines > self.max_removed:
                self.max_removed = self.cur_removed_lines
                # print("#########GAME OVER#########")
            return False

        if self.num_of_full_lines == 0:
            self.calculate()

        return True

    def remove_full_lines(self):
        # to_remove = np.argwhere(np.sum(self.board, axis=1) == Board.BOARD_WIDTH).ravel()

        if self.num_of_full_lines:
            self.calculate()
            self.num_of_full_lines = 0

        to_remove = np.nonzero(np.all(self.board, axis=1))[0]

        if len(to_remove) == 0:
            return

        self.__removed_points += len(to_remove) * self.BOARD_WIDTH

        self.one_removed_lines = len(to_remove)
        self.cur_removed_lines += len(to_remove)

        after_remove = np.delete(self.board, to_remove, axis=0)
        self.board = np.zeros((Board.BOARD_HEIGHT, Board.BOARD_WIDTH), np.int)
        np.copyto(self.board[0:after_remove.shape[0]], after_remove)

        self.board_m[1:] = self.BOARD_M_FULL[1:] * (self.board > 0)

    def calculate(self):
        top = np.argmax(self.board_m, axis=0)
        self.last_bad_pos = self.bad_pos
        self.bad_pos = np.sum(top) - np.sum(self.board > 0)
        self.last_var = self.var
        self.var = np.sum(np.abs(top[1:] - top[0:-1]))
        return self.bad_pos, self.var

    def print_info(self):
        print()
        print('#############################')
        print("Board:")
        pprint.pprint(self.board[::-1])
        # print("Features Vector:")
        # print(board.get_feature_vector().reshape((self.BOARD_WIDTH, self.GAME_OVER_HEIGHT + 1)))

        print("Last bad:%d, Bad:%d, Last Var:%d, Var:%d" % (self.last_bad_pos, self.bad_pos, self.last_var, self.var))
        print("Total Removed Lines:", self.total_removed_lines)
        print("Current Removed Lines:", self.cur_removed_lines)
        print("One Removed Lines:", self.one_removed_lines)
        print('#############################')
        print()


if __name__ == '__main__':
    board = Board()
    board.start_training()
    #
    # board.print_info()
    #
    # board.set_pos(0, 2, 2)
    # board.set_pos(0, 2, 3)
    # board.set_pos(1, 4, 5)
    # board.set_pos(2, 4, 6)
    # board.set_pos(3, 5, 3)
    # board.set_pos(4, 3, 1)
    # board.set_pos(5, 2, 2)
    # board.set_pos(6, 3, 2)
    # board.set_pos(7, 1, 4)
    # board.set_pos(8, 1, 5)
    # board.set_pos(9, 1, 1)
    # for i in range(10):
    #     board.set_pos(i, 0, 1)
    #     board.set_pos(i, 4, 4)
    #
    # board.calculate()
    # board.print_info()
    # board.remove_full_lines()
    # board.calculate()
    # board.print_info()
    # board.started = True
    # for i in range(10):
    #     shape = board.new_shape()
    #     shape.print_shape()
    #     board.add_shape(shape)
    #     board.print_info()
    #     if not board.started:
    #         break
