import sys

from PyQt5.QtCore import Qt, QTimer, QThread, pyqtSignal
from PyQt5.QtGui import QFont, QKeyEvent
from PyQt5.QtWidgets import (QApplication, QGridLayout, QHBoxLayout, QLabel,
                             QPushButton, QSizePolicy, QSpacerItem,
                             QVBoxLayout, QWidget)

# Custom modules
from main.actions import Action
from main.colors import Color, get_color_by_number, hex_to_rgba
from main.game_manager import GameManager
from model.model_thread import ModelThread, ProcessType


class GridWidget(QWidget):
    """ A widget that represents grid with labels. """
    
    def __init__(self, grid_width=10, grid_height=20):
        super().__init__()
        
        self.width = grid_width
        self.height = grid_height
        self.labels = {}
        rgba_value = hex_to_rgba(Color.GRAY.value, alpha=0.3)
        self.border_color = f"border: 1px solid rgba{rgba_value};"
        
        self._set_grid()

    def _set_grid(self):
        """ Sets grid built from QLabel widgets. """
        
        layout = QGridLayout(self)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        
        for row in range(self.height):
            for column in range(self.width):
                label = QLabel()
                label.setStyleSheet(self.border_color)
                layout.addWidget(label, row, column)
                self.labels[(row, column)] = label

        self.setLayout(layout)
    
    def get_label(self, row: int, column: int) -> QLabel:
        """ Gets grid's label at a specific row and column.

        Args:
            row (int): Row number
            column (int): Column number

        Returns:
            QLabel: Label widget that represents grid cell.
        """
        
        return self.labels[(row, column)]


class Tetris(QWidget):
    """ A classic Tetris game. """
    
    send_state = pyqtSignal(tuple)
    
    def __init__(self, train_ai: bool = False, player_ai: bool = False):
        super().__init__()

        self.train_ai = train_ai
        self.player_ai = player_ai
        
        self.model_thread = None
        self.height = 550
        self.width = 420
        self.left_panel_width = 300
        self.game_grid_width = 10
        self.game_grid_height = 20
        self.score_label = None
        self.game_layout = None
        self.game_grid_ui = None
        self.next_grid_ui = None
        self.manager = None
        self.background_color = "background-color: #333;"
        self.timer = None
        self.score = 0
        
        self._set_ui()
        self._set_game_grid_ui()
        self._set_next_piece_grid_ui()

    def _set_ui(self):
        """ Sets start window UI widgets. """
        
        self.setWindowTitle('Tetris')
        
        main_layout = QGridLayout(self)
        
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_panel.setStyleSheet(self.background_color)
        
        main_layout.addWidget(left_panel, 0, 0, -1, 1)
        
        next_panel = QWidget()
        next_layout = QVBoxLayout(next_panel)
        next_panel.setStyleSheet(self.background_color)
        next_layout.setAlignment(Qt.AlignTop | Qt.AlignHCenter)
        
        next_title_label = QLabel("NEXT")
        next_title_label.setFont(QFont('Arial', 12, QFont.Bold))
        next_title_label.setStyleSheet(f"color: {Color.WHITE.value};")
        next_title_label.setAlignment(Qt.AlignCenter)
        next_layout.addWidget(next_title_label)
        
        main_layout.addWidget(next_panel, 0, 1)
        
        score_panel = QWidget()
        score_layout = QVBoxLayout(score_panel)
        score_panel.setStyleSheet(self.background_color)
        score_layout.setAlignment(Qt.AlignTop | Qt.AlignHCenter)
        
        score_title_label = QLabel("SCORE")
        score_title_label.setFont(QFont('Arial', 12, QFont.Bold))
        score_title_label.setStyleSheet(f"color: {Color.WHITE.value};")
        score_title_label.setAlignment(Qt.AlignCenter)
        score_layout.addWidget(score_title_label)
        
        score_label = QLabel("")
        score_label.setFont(QFont('Arial', 12, QFont.Bold))
        score_label.setStyleSheet(f"color: {Color.WHITE.value};")
        score_label.setAlignment(Qt.AlignCenter)
        score_layout.addWidget(score_label)
        
        main_layout.addWidget(score_panel, 1, 1)
        
        spacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        main_layout.addItem(spacer, 2, 1)
        
        main_layout.setRowMinimumHeight(0, 100)
        main_layout.setRowMinimumHeight(1, 80)
        main_layout.setColumnMinimumWidth(0, self.left_panel_width)
        
        self.setLayout(main_layout)
        self.setGeometry(100, 100, self.width, self.height)
        
        self.game_layout = left_layout
        self.next_layout = next_layout
        self.score_label = score_label
    
    def _set_game_grid_ui(self):
        """ Sets game play grid widget. """
        
        grid_widget = GridWidget(grid_width=self.game_grid_width,
                                 grid_height=self.game_grid_height)
        
        self.game_layout.setContentsMargins(0, 0, 0, 0)
        self.game_layout.addWidget(grid_widget)
        self.game_grid_ui = grid_widget

    def _set_next_piece_grid_ui(self):
        """ Sets next piece grid widget. """
        
        grid_width = 5
        grid_height = 2
        
        # Smaller than game grid cells by 80%
        cell_width = int(self.left_panel_width / self.game_grid_width * 0.8)
        cell_height = int(self.height / self.game_grid_height * 0.8)
        
        grid_widget = GridWidget(grid_width=grid_width, grid_height=grid_height)
        grid_widget.setFixedSize(cell_width*grid_width, cell_height*grid_height)
        
        self.next_layout.setContentsMargins(0, 0, 0, 0)
        self.next_layout.addWidget(grid_widget)
        self.next_grid_ui = grid_widget
        
    def _draw_grid(self):
        for row in range(self.manager.board_height):
            for column in range(self.manager.board_width):
                label = self.game_grid_ui.get_label(row, column)
                value = self.manager.board[row][column]
                if value != 0:
                    color = get_color_by_number(value)
                    label.setStyleSheet(
                        f"background-color: {color}; {self.game_grid_ui.border_color}")
                else:
                    label.setStyleSheet(self.game_grid_ui.border_color)

    def _draw_next_grid(self):
        # Clear next grid
        for row in range(self.next_grid_ui.height):
            for column in range(self.next_grid_ui.width):
                label = self.next_grid_ui.get_label(row, column)
                label.setStyleSheet(self.next_grid_ui.border_color)

        # Draw the next piece
        for row, column in self.manager.next_piece.shape:
            label = self.next_grid_ui.get_label(row, column+1)
            label.setStyleSheet((
                f"background-color: {self.manager.next_piece.color};"
                f" {self.game_grid_ui.border_color}"
            ))
    
    def _set_game_sync(self):
        self.timer = QTimer(self)
        self.timer.timeout.connect(lambda: self.step(Action.DOWN.value))
        self.timer.start(1000)  # Update every second
    
    def _set_training(self):
        self.model_thread = ModelThread(self.game_grid_height,
                                        self.game_grid_width,
                                        ProcessType.TRAINING)
        
        self.model_thread.reset.connect(self.reset)
        self.model_thread.step.connect(self.step)
        
        self.send_state.connect(self.model_thread.receive_state)
        self.model_thread.start()
    
    def _set_playing(self):
        self.model_thread = ModelThread(self.game_grid_height,
                                        self.game_grid_width,
                                        ProcessType.PLAYING)
        
        self.model_thread.reset.connect(self.reset)
        self.model_thread.step.connect(self.step)
        
        self.send_state.connect(self.model_thread.receive_state)
        self.model_thread.start()
    
    def keyPressEvent(self, event: QKeyEvent):
        """ Captures user's key presses and defines specific actions
        for each key.

        Args:
            event (QKeyEvent): Contains information about the key event.
        """
        
        if self.train_ai or self.player_ai:
            return
        
        if event.key() == Qt.Key_Left:
            self.step(Action.LEFT.value)
        elif event.key() == Qt.Key_Right:
            self.step(Action.RIGHT.value)
        elif event.key() == Qt.Key_Up:
            self.step(Action.UP.value)
        elif event.key() == Qt.Key_Down:
            self.step(Action.DOWN.value)
        elif event.key() == Qt.Key_Escape:
            self.step(Action.EXIT.value)
    
    def reset(self):
        """ Sets the game's initial state. """
        
        self.score = 0
        
        if not self.manager:
            self.manager = GameManager(used_in_gui=True)
            
        self.manager.reset()
        
        if not self.timer:
            self._set_game_sync()

        if not self.model_thread:
            if self.train_ai:
                self._set_training()
            elif self.player_ai:
                self._set_playing()
        
        if self.model_thread:
            self.send_state.emit((self.manager.board, 0, False))
        
    def step(self, action: int) -> tuple:
        """ Updates environment according to given action.

        Args:
            action (int): In game action value.
        """
        
        game_over = False
        filled_lines = 0
        ai_score = 0
                
        if action == Action.LEFT.value:
            self.manager.move_left()
        elif action == Action.RIGHT.value:
            self.manager.move_right()
        elif action == Action.UP.value:
            self.manager.rotate()
        elif action == Action.DOWN.value:
            is_down = self.manager.move_down()
            if is_down:
                if not self.train_ai and not self.player_ai:
                    filled_lines = self.manager.clear_filled_lines() * 100
                    self.score += filled_lines
                if self.manager.is_game_over():
                    game_over = True
        elif action == Action.EXIT.value:
            self.close()

        self.score_label.setText(str(self.score))
        self._draw_next_grid()
        self._draw_grid()
        
        if self.train_ai or self.player_ai:
            ai_score = self.manager.get_score()
            self.send_state.emit((self.manager.board, ai_score, game_over))
        
        return self.manager.board, filled_lines, game_over


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = Tetris()
    window.reset()
    window.show()
    sys.exit(app.exec_())
