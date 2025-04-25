import sys
from PyQt5.QtWidgets import QApplication

from environment import Tetris


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = Tetris(train_ai=True)
    window.reset()
    window.show()
    sys.exit(app.exec_())
        