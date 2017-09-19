import random

import numpy as np
import pickle
import time
from Shape import Shape


class QLearnPlayer(object):
    SHAPES = [Shape(i) for i in range(Shape.MAX_SHAPE)]

    def __init__(self):
        self.alpha = 0.02
        self.gamma = 0.8
        self.epsilon = 0.01
        self.theta = None

        self.cur_status = None
        self.cur_shape = None
        self.cur_action = None

        self.debug = False
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
            # if self.debug:
            print("Random Action:", self.cur_action)
        else:
            self.cur_action = self.best_action(feature, shape)[0]
        return self.cur_action

    def best_action(self, status, shape):
        m = -(10 ** 10)
        result = (0, 0)
        actions = shape.get_actions()

        for action_1 in range(len(actions)):
            for action_2 in actions[action_1]:
                t = np.sum(self.theta[shape.get_shape()][action_1][action_2] * status)
                if self.debug:
                    print(status, shape.get_name(), action_1, action_2, t)
                if t > m:
                    m = t
                    result = (action_1, action_2)
        if self.debug:
            print("best:", m, result)

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
        if self.debug:
            print(self.cur_status, ":", self.cur_shape.get_name(), ":", self.cur_action, ":", "reward", reward)

        if not self.learn:
            return

        this_q = np.sum(
            self.theta[self.cur_shape.get_shape()][self.cur_action[0]][self.cur_action[1]] * self.cur_status)
        next_q = 0
        for p_shape in range(1, Shape.MAX_SHAPE):
            next_action, max_q = self.best_action(new_status, QLearnPlayer.SHAPES[p_shape])
            next_q += max_q
        next_q /= (Shape.MAX_SHAPE - 1)

        t = self.alpha * (reward + self.gamma * next_q - this_q)
        a = t * np.float64(self.cur_status)
        self.theta[self.cur_shape.get_shape()][self.cur_action[0]][self.cur_action[1]] += a


if __name__ == '__main__':
    player = QLearnPlayer()
    player.set_features(10, [8, 4, 10])
    # player.set_debug(True, True)
    s1 = Shape(3)
    for i in range(1000):
        player.select_action([1 for i in range(10)], s1)
        player.update([2 for i in range(10)], -1)
        player.select_action([1 for i in range(10)], s1)
        player.update([2 for i in range(10)], 2)
        player.select_action([1 for i in range(10)], s1)


