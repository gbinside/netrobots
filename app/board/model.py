class Board:
    def __init__(self, size=(1000, 1000)):
        self._size = size
        self.robots = {}
        self._missiles = []
        self._explosions = []

    def reinit(self, size=(1000, 1000)):
        self.__init__(size)

    def get_status(self):
        return dict(
            size=self._size,
            robots=dict(self.robots),
            missiles=list(self._missiles),
            explosions=list(self._explosions),
        )