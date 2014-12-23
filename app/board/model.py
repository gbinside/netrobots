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

    def radar(self, scanning_robot, xy, max_scan_distance, degree, resolution):
        ret = []
        for robot in [x for x in self.robots.values() if x != scanning_robot]:
            distance, angle = robot.distance(xy)
            if angle > degree + resolution or angle < degree - resolution:
                continue
            if distance > max_scan_distance:
                continue
            ret.append(distance)
        return min(ret) if ret else 0
