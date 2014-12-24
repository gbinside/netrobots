class Board:
    def __init__(self, size=(1000, 1000)):
        self._size = size
        self.robots = {}
        self._missiles = []
        self._explosions = []
        self._wall_hit_damage = 2

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

    def detect_collision(self, robot, xy, dxy):
        x, y = xy
        dx, dy = dxy
        # COLLISION WITH WALLS
        if x < 0:
            y = y - dy * x / dx
            x = 0
            return x, y, self._wall_hit_damage
        if x > self._size[0]:
            y = y - dy * (x - self._size[0]) / dx
            x = self._size[0]
            return x, y, self._wall_hit_damage
        if y < 0:
            x = x - dx * y / dy
            y = 0
            return x, y, self._wall_hit_damage
        if y > self._size[1]:
            x = x - dx * (y - self._size[1]) / dy
            y = self._size[1]
            return x, y, self._wall_hit_damage
        # @TODO collision with other robots
        return None

    def join(self, robot):
        return True