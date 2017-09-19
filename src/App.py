import sys
from PyQt5.QtWidgets import QMainWindow, QDesktopWidget, QApplication
from Board import Board

class App(QMainWindow):
    def __init__(self):
        super().__init__()

        self.WIDTH = 360
        self.HEIGHT = 760

        self.board = Board(self)
        self.status_bar = self.statusBar()
        self.board.msg_2_bar[str].connect(self.status_bar.showMessage)

        self.setCentralWidget(self.board)
        self.resize(self.WIDTH, self.HEIGHT)
        self.center()
        self.setWindowTitle('Tetris')
        self.show()

    def center(self):
        screen = QDesktopWidget().screenGeometry()
        size = self.geometry()
        self.move((screen.width() - size.width()) / 2,
                  (screen.height() - size.height()) / 2)


if __name__ == '__main__':
    qApp = QApplication([])
    app = App()
    sys.exit(qApp.exec_())
