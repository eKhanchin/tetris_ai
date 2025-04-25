import numpy

class Grid:
    """ A class that represents board grid in the Tetris game. """
    
    def __init__(self, width=10, height=20):
        self.width = width
        self.height = height
        
        self.board = numpy.zeros((self.height, self.width), dtype=numpy.int32)
