from math import atan2, degrees, pi

START_COORDS = [(250, 500), (750, 500), (500, 250), (500, 750), (250, 250), (750, 750), (750, 250), (250, 750)]
START_HEADING = [0, 180, 90, 270, 45, 225, 135, 315]


class Robot:
    def __init__(self, board, name, count_of_other=0):
        self._board = board
        self._name = name
        self._hit_points = 100
        self._winner = False
        self._dead = False
        self._x, self._y = START_COORDS[count_of_other % len(START_COORDS)]
        self._heading = START_HEADING[count_of_other % len(START_HEADING)]
        self._current_speed = 0
        self._required_speed = 0
        self._max_speed = 100
        self._acceleration = 40
        self._decelleration = 40
        self._max_sterling_speed = 50
        self._max_scan_distance = 700
        self._max_fire_distance = 700
        self._bullet_speed = 400
        """
        3%  --    A missile explodes within a 40 meter radius.
        5%  --    A missile explodes within a 20 meter radius.
        10% --    A missile explodes within a 5 meter radius.
        """
        self._bullet_damage = ((40, 3), (20, 5), (5, 10))
        self._reloading = False
        self._reloading_time = 2
        self._reloading_counter = 0
        self._max_actions = 1
        self._current_actions = 0

    def get_status(self):
        return dict(
            name=self._name,
            hp=self._hit_points,
            heading=self._heading,
            speed=self._current_speed,
            x=self._x,
            y=self._y,
            dead=self._dead,
            winner=self._winner,
            max_speed=self._max_speed,
            reloading=self._reloading
        )

    def drive(self, degree, speed):
        if self._can_act():
            degree, speed = int(degree), int(speed)
            if self._current_speed <= self._max_sterling_speed:
                self._heading = degree
                self._required_speed = min(speed, self._max_speed)
            else:
                # overheat
                self._current_speed = 0
                self._required_speed = 0
            self._act_done()
            return True
        return None

    def _can_act(self):
        return self._current_actions < self._max_actions

    def _act_done(self):
        self._current_actions += 1

    def scan(self, degree, resolution):
        if self._can_act():
            degree, resolution = int(degree), int(resolution)
            distance = self._board.radar(self, (self._x, self._y), self._max_scan_distance, degree, resolution)
            self._act_done()
            return distance
        return None

    def cannon(self, degree, distance):
        if self._can_act():
            degree, distance = int(degree), min(int(distance), self._max_fire_distance)
            # @todo fire a missile class
            self._reloading = True
            self._act_done()
            return True
        return None

    def distance(self, xy):
        dx = (self._x - xy[0])
        dy = (self._y - xy[1])
        dist = (dx ** 2 + dy ** 2) ** 0.5
        rads = atan2(-dy, dx)
        rads %= 2 * pi
        angle = degrees(rads)
        return dist, angle
