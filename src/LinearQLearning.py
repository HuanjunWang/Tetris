import random

import numpy as np
import pickle
import time
from Shape import Shape


class QLearnPlayer(object):
    SHAPES = [Shape(i) for i in range(Shape.MAX_SHAPE)]

    DEBUG_LEVEL0 = 0
    DEBUG_LEVEL1 = 1
    DEBUG_LEVEL2 = 2
    DEBUG_LEVEL3 = 3

    def __init__(self):
        self.alpha = 0.02
        self.gamma = 0.8
        self.epsilon = 0.02
        self.theta = None

        self.cur_status = None
        self.cur_shape = None
        self.cur_action = None

        self.debug = 0
        self.learn = True

    def set_features(self, features_num, categories):
        self.theta = []
        for c1 in range(categories[0]):
            self.theta.append([])
            for c2 in range(categories[1]):
                self.theta[c1].append([])
                for c3 in range(categories[2]):
                    self.theta[c1][c2].append(np.zeros(features_num, np.float))

    def set_debug(self, debug, learn):
        self.debug = debug
        self.learn = learn

    def select_action(self, feature, shape):
        self.cur_status = feature
        self.cur_shape = shape
        if self.learn and random.random() < self.epsilon:
            actions = shape.get_actions()
            a1 = random.randint(0, len(actions) - 1)
            a2 = random.choice(actions[a1])
            self.cur_action = (a1, a2)
            if self.debug >= self.DEBUG_LEVEL1:
                print("Random Action:", self.cur_action)
        else:
            self.cur_action, val = self.best_action(feature, shape)
            if self.debug >= self.DEBUG_LEVEL1:
                print("Select Action ", self.cur_action, val)
        return self.cur_action

    def best_action(self, status, shape):
        m = -(10 ** 10)
        result = (0, 0)
        actions = shape.get_actions()

        for action_1 in range(len(actions)):
            for action_2 in actions[action_1]:
                t = np.sum(self.theta[shape.get_shape()][action_1][action_2] * status)
                if self.debug >= self.DEBUG_LEVEL3:
                    print(shape.get_name(), action_1, action_2, t)
                if t > m:
                    m = t
                    result = (action_1, action_2)
        if self.debug >= self.DEBUG_LEVEL3:
            print("Best Action:", shape.get_name(), m, result)

        return result, m

    def save_theta(self):
        file_name = "theta" + time.strftime("%Y_%b_%d_%H_%M_%S")
        with open("theta.save", 'wb') as f:
            pickle.dump(self.theta, f)
        with open(file_name, 'wb') as f:
            pickle.dump(self.theta, f)

    def load_theta(self, file_name=None):
        if file_name is None:
            file_name = "theta.save"
        with open(file_name, 'rb') as f:
            self.theta = pickle.load(f)

    def update(self, new_status, reward):
        if self.debug >= self.DEBUG_LEVEL1:
            print("Update:", self.cur_shape.get_name(), ":",
                  self.cur_action, ":", "reward", reward)

        if not self.learn:
            return

        this_q = np.sum(
            self.theta[self.cur_shape.get_shape()][self.cur_action[0]][self.cur_action[1]] * self.cur_status)
        next_q = 0

        # for p_shape in range(1, Shape.MAX_SHAPE):
        p_shape = Shape.SquareShape
        next_action, max_q = self.best_action(new_status, QLearnPlayer.SHAPES[p_shape])
        next_q += max_q
        # next_q /= (Shape.MAX_SHAPE - 1)

        if self.debug >= self.DEBUG_LEVEL2:
            print("Update this: %f next: %f " % (this_q, next_q))

        t = self.alpha * (reward + self.gamma * next_q - this_q)
        a = np.array(self.cur_status) * t
        self.theta[self.cur_shape.get_shape()][self.cur_action[0]][self.cur_action[1]] += a


if __name__ == '__main__':
    player = QLearnPlayer()
    player.set_features(10, [8, 4, 10])
    player.set_debug(QLearnPlayer.DEBUG_LEVEL2, True)
    s1 = Shape(3)
    for i in range(100000):
        player.select_action([1 for i in range(10)], s1)
        player.update([2 for i in range(10)], 1)
