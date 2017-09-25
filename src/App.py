import sys
import threading
import time

from PyQt5.QtGui import QPainter, QColor, QFont
from PyQt5.QtWidgets import QMainWindow, QDesktopWidget, QApplication
from PyQt5.QtCore import Qt, QBasicTimer, pyqtSignal
from qtpy import QtWidgets

from Board import Board
from Shape import Shape
from LinearQLearning import QLearnPlayer


def catch_exceptions(t, val, tb):
    QtWidgets.QMessageBox.critical(None,
                                   "An exception was raised",
                                   "Exception type: {}".format(t))
    old_hook(t, val, tb)


old_hook = sys.excepthook
sys.excepthook = catch_exceptions


class App(QMainWindow):
    RUNNING_MODE_NONE = 4
    RUNNING_MODE_PLAY = 1
    RUNNING_MODE_TRAINING = 2
    RUNNING_MODE_AI_PLAY = 3
    RUNNING_MODE_REPLAY = 4

    DEFAULT_SPEED = 300

    FONT_BIG = 40
    FONT_M = 25
    FONT_SMALL = 16

    msg_2_bar = pyqtSignal(str)

    def __init__(self):
        super().__init__()

        self.status_bar = self.statusBar()
        self.msg_2_bar[str].connect(self.status_bar.showMessage)
        self.board_msg = None

        self.WIDTH = 360
        self.HEIGHT = 740
        self.STATUS_BAR_HEIGHT = 20
        self.GAME_OVER_LINE_HEIGHT = self.HEIGHT - self.STATUS_BAR_HEIGHT \
                                     - (self.square_width() * Board.GAME_OVER_HEIGHT)

        self.resize(self.WIDTH, self.HEIGHT)
        self.center()
        self.setWindowTitle('Tetris')
        self.show()

        self.timer = QBasicTimer()
        self.speed = self.DEFAULT_SPEED

        self.board = Board()
        self.running = False
        self.running_mode = self.RUNNING_MODE_NONE
        self.show_board_msg([(self.FONT_M, 1, 'Press Any Key'), (self.FONT_M, 1, 'To Start')])
        self.show_status_bar_msg('Press T to Training, Press A to show AI')

        self.player = None

    def show_board_msg(self, msg):
        self.board_msg = msg

    def clear_board_msg(self):
        self.board_msg = None

    def show_status_bar_msg(self, msg):
        self.msg_2_bar.emit(str(msg))

    def center(self):
        screen = QDesktopWidget().screenGeometry()
        size = self.geometry()
        self.move((screen.width() - size.width()) / 2,
                  (screen.height() - size.height()) / 2)

    def paintEvent(self, event):
        painter = QPainter(self)

        painter.setPen(QColor(0xff0000))
        painter.drawLine(0, self.GAME_OVER_LINE_HEIGHT, self.WIDTH, self.GAME_OVER_LINE_HEIGHT)
        painter.drawLine(0, self.GAME_OVER_LINE_HEIGHT + 2, self.WIDTH, self.GAME_OVER_LINE_HEIGHT + 2)

        board_bottom = self.height() - self.STATUS_BAR_HEIGHT
        for i in range(Board.BOARD_HEIGHT):
            for j in range(Board.BOARD_WIDTH):
                shape = self.board.board[i, j]
                if shape != Shape.NoShape:
                    self.draw_square(painter, j * self.square_width(),
                                     board_bottom - (i + 1) * self.square_height(), shape)

        if self.board.cur_shape and self.board.cur_shape.get_shape() != Shape.NoShape:
            for y, x in self.board.cur_shape.get_pos():
                j = self.board.cur_y - y
                self.draw_square(painter, x * self.square_width(),
                                 board_bottom - (j + 1) * self.square_height(), self.board.cur_shape.get_shape())

        if self.board_msg:
            color_table = [0x000000, 0xCC6666, 0x66CC66, 0x6666CC,
                           0xCCCC66, 0xCC66CC, 0x66CCCC, 0xDAAA00]
            y = 300
            for msg in self.board_msg:
                painter.setFont(QFont("Consolas", msg[0]))
                painter.setPen(QColor(color_table[msg[1]]))
                painter.drawText(10, y, msg[2])
                y += 100

    def draw_square(self, painter, x, y, shape):
        color_table = [0x000000, 0xFF0000, 0x66FF66, 0x6666CC,
                       0xCCCC66, 0xCC66CC, 0x66CCCC, 0xDAAA00]

        color = QColor(color_table[shape])
        painter.fillRect(x + 1, y + 1, self.square_width() - 2,
                         self.square_height() - 2, color)

        painter.setPen(color.lighter())
        painter.drawLine(x, y + self.square_height() - 1, x, y)
        painter.drawLine(x, y, x + self.square_width() - 1, y)

        painter.setPen(color.darker())
        painter.drawLine(x + 1, y + self.square_height() - 1,
                         x + self.square_width() - 1, y + self.square_height() - 1)
        painter.drawLine(x + self.square_width() - 1,
                         y + self.square_height() - 1, x + self.square_width() - 1, y + 1)

    def square_width(self):
        return self.WIDTH / Board.BOARD_WIDTH

    def square_height(self):
        return self.square_width()

    def start_play(self):
        self.running_mode = self.RUNNING_MODE_PLAY
        self.clear_board_msg()

        self.board.init()
        self.board.next_step()
        self.update()
        self.timer.start(self.speed, self)

    def timerEvent(self, event):
        if event.timerId() == self.timer.timerId():
            self.next_step()

    def start_training(self):
        pass

    def start_ai(self):
        self.running_mode = self.RUNNING_MODE_AI_PLAY
        self.clear_board_msg()
        self.replay = []
        threading.Thread(target=self.ai_thread).start()

    def start_replay(self):
        self.running_mode = self.RUNNING_MODE_REPLAY
        self.clear_board_msg()

        self.board.init()
        self.update()

        player = QLearnPlayer()
        player.load_theta('16_theta_14')
        player.set_debug(debug=player.DEBUG_LEVEL3, learn=False)
        self.player = player


    def replay_next(self):
        # threading.Thread(target=self.replay_thread()).start()
        threading.Thread(target=self.replay_thread).start()
        pass

    def replay_thread(self):
        # self.board.new_shape(self.replay.pop(0).piece_shape)
        self.board.new_shape()
        self.update()
        time.sleep(self.speed / 1000.0)

        action = self.player.select_action(self.board.get_feature_vector(), self.board.cur_shape)
        self.board.cur_shape.set_sub_shape(action[0])
        self.board.cur_shape.set_x(action[1])
        self.update()

        if not self.board.add_shape_without_remove():
            self.update()
            self.game_over()

        if self.board.num_of_full_lines:
            time.sleep(1)
            self.board.remove_full_lines()
            self.update()

        self.show_status_bar_msg("Score:%d" % self.board.cur_removed_lines)
        print(self.board.get_reward())

    def replay_pre(self):
        pass

    def ai_thread(self):
        self.board.init()
        player = QLearnPlayer()
        player.load_theta('16_theta_14')
        player.set_debug(debug=player.DEBUG_LEVEL0, learn=False)

        while self.running:
            self.replay.append(self.board.new_shape())
            self.update()
            time.sleep(float(self.speed) / 1000)
            action = player.select_action(self.board.get_feature_vector(), self.board.cur_shape)
            self.board.cur_shape.set_sub_shape(action[0])
            self.board.cur_shape.set_x(action[1])
            self.update()

            if not self.board.add_shape_without_remove():
                self.game_over()
                time.sleep(1)
                self.update()
                break

            if self.board.num_of_full_lines:
                time.sleep(float(self.speed) / 1000)
                self.board.remove_full_lines()
                self.update()

            self.show_status_bar_msg("Score:%d" % self.board.cur_removed_lines)

    def keyPressEvent(self, event):
        key = event.key()
        if not self.running:
            self.running = True

            if key == Qt.Key_T:
                self.start_training()
                return

            if key == Qt.Key_A:
                self.start_ai()
                return

            if key == Qt.Key_R:
                self.start_replay()
                return

            self.start_play()

        else:
            if self.running_mode == self.RUNNING_MODE_AI_PLAY:
                self.handle_ai_play_key(key)
            elif self.running_mode == self.RUNNING_MODE_PLAY:
                self.handle_play_key(key)
            elif self.running_mode == self.RUNNING_MODE_TRAINING:
                self.handle_training_key()
            elif self.running_mode == self.RUNNING_MODE_REPLAY:
                self.handle_replay_key(key)

    def handle_ai_play_key(self, key):
        if key == Qt.Key_S:
            self.game_over()
            self.update()

        elif key == Qt.Key_Up:
            self.speed *= 2
        elif key == Qt.Key_Down:
            self.speed /= 2

    def handle_replay_key(self, key):
        if key == Qt.Key_N or key == Qt.Key_Right:
            self.replay_next()
        elif key == Qt.Key_P or key == Qt.Key_Left:
            self.replay_pre()

    def handle_training_key(self, key):
        pass

    def handle_play_key(self, key):
        if key == Qt.Key_F:
            self.speed /= 2
            self.timer.stop()
            self.timer.start(self.speed, self)

        elif key == Qt.Key_S:
            self.speed *= 2
            self.timer.stop()
            self.timer.start(self.speed, self)

        elif key == Qt.Key_Left:
            self.board.move_left()
            self.update()

        elif key == Qt.Key_Right:
            self.board.move_right()
            self.update()

        elif key == Qt.Key_Down:
            self.board.rotate_left()
            self.update()

        elif key == Qt.Key_Up:
            self.board.rotate_right()
            self.update()

        elif key == Qt.Key_Space:
            self.next_step(True)

    def next_step(self, fast=False):
        if self.board.next_step(fast):
            self.show_status_bar_msg("Score:%d" % self.board.cur_removed_lines)
            if fast:
                self.board.next_step(fast=False)
        else:
            self.game_over()
        self.update()

    def game_over(self):
        self.running = False
        self.running_mode = self.RUNNING_MODE_NONE

        self.show_board_msg([[self.FONT_BIG, 1, 'GAME OVER'],
                             [self.FONT_M, 0, "Score: %d" % self.board.cur_removed_lines]])

        self.board.point_check()

        self.show_status_bar_msg("Game Over")

        if self.timer.isActive():
            self.timer.stop()


if __name__ == '__main__':
    qApp = QApplication([])
    app = App()
    app.show()
    sys.exit(qApp.exec_())
