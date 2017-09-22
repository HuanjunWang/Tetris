import sys
import threading

import time
from PyQt5.QtGui import QPainter, QColor, QFont
from PyQt5.QtWidgets import QMainWindow, QDesktopWidget, QApplication
from PyQt5.QtCore import Qt, QBasicTimer, pyqtSignal
from Board import Board
from Shape import Shape
from LinearQLearning import QLearnPlayer


class App(QMainWindow):
    NONE = 4
    PLAY = 1
    TRAINING = 2
    AI_PLAY = 3
    DEFAULT_SPEED = 300

    FONT_BIG = 40
    FONT_M = 25
    FONT_SMALL = 16
    msg_2_bar = pyqtSignal(str)

    def __init__(self):
        super().__init__()

        self.status_bar = self.statusBar()
        self.msg_2_bar[str].connect(self.status_bar.showMessage)
        self.status_bar_height = 20

        self.WIDTH = 360
        self.HEIGHT = 760
        self.resize(self.WIDTH, self.HEIGHT)
        self.center()
        self.setWindowTitle('Tetris')
        self.show()

        self.board = Board()
        self.board.init()

        self.timer = QBasicTimer()
        self.speed = self.DEFAULT_SPEED

        self.running = False
        self.mode = self.NONE

        self.board_msg = None
        self.status_bar_msg('Press T to Training, Press A to show AI')
        self.show_msg([(self.FONT_SMALL, 2, 'Press Any Key To Start')])

    def show_msg(self, msg):
        self.board_msg = msg

    def clear_msg(self):
        self.board_msg = None

    def status_bar_msg(self, msg):
        self.msg_2_bar.emit(str(msg))

    def center(self):
        screen = QDesktopWidget().screenGeometry()
        size = self.geometry()
        self.move((screen.width() - size.width()) / 2,
                  (screen.height() - size.height()) / 2)

    def paintEvent(self, event):
        painter = QPainter(self)

        game_over_line = self.height() - (self.square_width() * Board.GAME_OVER_HEIGHT) - self.status_bar_height
        painter.setPen(QColor(0xff0000))
        painter.drawLine(0, game_over_line, self.width(), game_over_line)

        board_bottom = self.height() - self.status_bar_height
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
        return self.width() / Board.BOARD_WIDTH

    def square_height(self):
        return self.square_width()

    def start_play(self):
        self.mode = self.PLAY
        self.clear_msg()

        self.board.init()
        self.board.new_shape()
        self.update()
        self.timer.start(self.speed, self)

    def start_training(self):
        pass

    def ai_thread(self):
        self.board.init()
        player = QLearnPlayer()
        player.load_theta('../../theta/theta_0.800000_0.020000_0.001000__2017_Sep_21_09_00_20')
        player.set_debug(debug=player.DEBUG_LEVEL0, learn=False)

        while self.running:
            self.board.new_shape()
            self.update()
            time.sleep(float(self.speed) / 1000)
            action = player.select_action(self.board.get_feature_vector(), self.board.cur_shape)
            self.board.cur_shape.set_sub_shape(action[0])
            self.board.cur_shape.set_x(action[1])
            self.update()

            if not self.board.add_shape(self.board.cur_shape):
                self.game_over()
                time.sleep(1)
                self.update()
                break

            self.status_bar_msg("Score:%d" % self.board.cur_removed_lines)

    def start_ai(self):
        self.mode = self.AI_PLAY
        self.clear_msg()
        threading.Thread(target=self.ai_thread).start()

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
            # Any other keys
            self.start_play()

        else:
            if self.mode == self.AI_PLAY:
                self.handle_ai_play_key(key)
            elif self.mode == self.PLAY:
                self.handle_play_key(key)
            elif self.mode == self.TRAINING:
                self.handle_training_key()

    def handle_ai_play_key(self, key):
        if key == Qt.Key_S:
            self.game_over()
            self.update()

        elif key == Qt.Key_Up:
            self.speed *= 2
        elif key == Qt.Key_Down:
            self.speed /= 2

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
        if not self.board.next_step(fast):
            self.game_over()
        else:
            self.status_bar_msg("Score:%d" % self.board.cur_removed_lines)
        self.update()

    def game_over(self):
        self.running = False
        self.mode = self.NONE

        self.show_msg([[self.FONT_BIG, 1, 'GAME OVER'],
                       [self.FONT_M, 0, "Score: %d" % self.board.cur_removed_lines]])

        self.status_bar_msg("Game Over")
        if self.timer.isActive():
            self.timer.stop()

    def timerEvent(self, event):
        if event.timerId() == self.timer.timerId():
            self.next_step()


if __name__ == '__main__':
    qApp = QApplication([])
    app = App()
    sys.exit(qApp.exec_())
