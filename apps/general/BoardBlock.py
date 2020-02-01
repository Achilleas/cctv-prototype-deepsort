class BoardBlock():
    """
    Default board parent class
    """
    def __init__(self, board):
        self.board = board

    def setup_callbacks(self):
        """
        Setup callbacks of the board
        """
        if self.board is not None and hasattr(self, 'callbacks'):
            self.callbacks(self.board)
