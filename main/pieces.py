from main.colors import Color


class Piece:
    """ A class that represents a playable piece in the Tetris game. """
    
    def __init__(self, color: str, shape: list, pivot_index: int):
        self.color = color
        self.shape = shape
        self.pivot_index = pivot_index
    
    def get_pivot_cell(self) -> list:
        """ Gets a pivot cell of the shape. """
        
        if self.pivot_index == -1:
            # No need to rotate
            return []
        
        return self.shape[self.pivot_index]


def create_game_pieces() -> list[Piece]:
    """Creates game\'s pieces.
    
    Parameters
    ----------
        colors : dictionary
            A dictionary of colors - name: color
    
    Returns
    -------
        pieces : list
            A list of game\'s pieces
    """

    pieces = []

    # #   ##
    # # ######     
    # shape = [[0, 1], [1, 0], [1, 1], [1, 2]]
    # pivot_index = 2
    # pieces.append(Piece(Color.PURPLE.value, shape, pivot_index))

    # #     ##
    # # ######
    # shape = [[0, 2], [1, 0], [1, 1], [1, 2]]
    # pivot_index = 2
    # pieces.append(Piece(Color.ORANGE.value, shape, pivot_index))

    # #   ####
    # # ####
    # shape = [[0, 1], [0, 2], [1, 0], [1, 1]]
    # pivot_index = 3
    # pieces.append(Piece(Color.GREEN.value, shape, pivot_index))

    # # ##
    # # ######
    # shape = [[0, 0], [1, 0], [1, 1], [1, 2]]
    # pivot_index = 2
    # pieces.append(Piece(Color.BLUE.value, shape, pivot_index))

    # # ####
    # #   ####
    # shape = [[0, 0], [0, 1], [1, 1], [1, 2]]
    # pivot_index = 2
    # pieces.append(Piece(Color.RED.value, shape, pivot_index))

    # ####
    # ####
    shape = [[0, 0], [0, 1], [1, 0], [1, 1]]
    pivot_index = -1
    pieces.append(Piece(Color.YELLOW.value, shape, pivot_index))

    # # ########
    # shape = [[0, 0], [0, 1], [0, 2], [0, 3]]
    # pivot_index = 2
    # pieces.append(Piece(Color.CYAN.value, shape, pivot_index))
    
    return pieces
