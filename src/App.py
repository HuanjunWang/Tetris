import sys
from PyQt5.QtGui import QPainter, QColor
from PyQt5.QtWidgets import QMainWindow, QDesktopWidget, QApplication
from Board import Board
from Shape import Shape


class App(QMainWindow):
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
        self.board.next_step()
        self.board.next_step()
        self.board.next_step()
        self.board.next_step()
        self.show_message('Hello')

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


if __name__ == '__main__':
    qApp = QApplication([])
    app = App()
    sys.exit(qApp.exec_())
