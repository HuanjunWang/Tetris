import sys
from PyQt5.QtGui import QPainter, QColor, QFont
from PyQt5.QtWidgets import QMainWindow, QDesktopWidget, QApplication
from PyQt5.QtCore import Qt, QBasicTimer
from Board import Board
from Shape import Shape


class App(QMainWindow):
    NONE = 4
    PLAY = 1
    TRAINING = 2
    AI_PLAY = 3

    DEFAULT_SPEED = 500

    def __init__(self):
        super().__init__()

        self.status_bar = self.statusBar()
        self.status_bar_height = 20

        self.WIDTH = 360
        self.HEIGHT = 760
        self.resize(self.WIDTH, self.HEIGHT)
        self.center()
        self.setWindowTitle('Tetris')
        self.show()
        self.board = Board()
        self.board.init()
        # self.board.next_step()
        self.show_message('T/A/Space')

        self.running = False
        self.mode = self.NONE
        self.timer = QBasicTimer()
        self.speed = self.DEFAULT_SPEED
        self.board_msg = None

    def show_message(self, msg):
        self.status_bar.showMessage(msg)

    def center(self):
        screen = QDesktopWidget().screenGeometry()
        size = self.geometry()
        self.move((screen.width() - size.width()) / 2,
                  (screen.height() - size.height()) / 2)

    def paintEvent(self, event):
        painter = QPainter(self)

        game_over = self.height() - (self.square_width() * Board.GAME_OVER_HEIGHT) - self.status_bar_height
        painter.setPen(QColor(0xff0000))
        painter.drawLine(0, game_over, self.width(), game_over)

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
            painter.setFont(QFont("Consolas", 40))
            painter.setPen(QColor(0xff0000))
            y = 200
            for msg in self.board_msg:
                painter.drawText(10, y, msg)
                y += 100

    def draw_square(self, painter, x, y, shape):
        color_table = [0x000000, 0xCC6666, 0x66CC66, 0x6666CC,
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
        self.board.init()
        self.mode = self.PLAY
        self.board_msg = None
        self.board.new_shape()
        self.update()
        self.timer.start(self.speed, self)

    def start_training(self):
        pass

    def start_ai(self):
        pass

    def keyPressEvent(self, event):
        key = event.key()
        if not self.running:

            if key == Qt.Key_Space:
                self.running = True
                self.start_play()
                return

            if key == Qt.Key_T:
                self.start_training()
                return

            if key == Qt.Key_A:
                self.start_ai()
            return
        else:
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
                print("Fast")
                if not self.board.move_down(0):
                    self.game_over()
                else:
                    self.board.new_shape()

                self.update()

    def game_over(self):
        self.running = False
        msg2 = "MAX %d" % self.board.cur_removed_lines
        self.board_msg = ["GAME OVER ", msg2]

        self.timer.stop()

    def timerEvent(self, event):
        if event.timerId() == self.timer.timerId():
            if not self.board.next_step(False):
                self.game_over()
            self.update()


if __name__ == '__main__':
    qApp = QApplication([])
    app = App()
    sys.exit(qApp.exec_())
