from math import atan2, degrees, pi, sin, cos, radians
from random import randint
import app

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
        self._max_speed = 27  # m/s
        self._acceleration = 9  # m/s^2
        self._decelleration = -5  # m/s^2
        self._max_sterling_speed = 13
        self._max_scan_distance = 700
        self._max_fire_distance = 700
        self._bullet_speed = 500  # m/s
        """
        3%  --    A missile explodes within a 40 meter radius.
        5%  --    A missile explodes within a 20 meter radius.
        10% --    A missile explodes within a 5 meter radius.
        """
        # self._bullet_damage = ((40, 3), (20, 5), (5, 10))
        # changed to progessive damage
        self._bullet_damage = ((40, 3), (20, 2), (5, 5))
        self._reloading = False
        self._reloading_time = 2  # s
        self._reloading_counter = 0.0

        if not app.app.config['TESTING']:
            self._x, self._y = randint(100, 900), randint(100, 900)

        self._board.add_robot(self)

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
        if self.is_dead():
            return False
        degree, speed = int(float(degree)) % 360, int(speed)
        if degree != self._heading and self._current_speed > self._max_sterling_speed:
            # overheat
            self.block()
        else:
            self._heading = degree
            self._required_speed = min(speed, self._max_speed)
        return True

    def scan(self, degree, resolution):
        if self.is_dead():
            return False
        degree, resolution = int(degree) % 360, max(1, int(resolution))
        distance = self._board.radar(self, (self._x, self._y), self._max_scan_distance, degree, resolution)
        return distance

    def cannon(self, degree, distance):
        if self.is_dead():
            return False
        if self._reloading is False:
            degree, distance = int(degree) % 360, min(int(float(distance)), self._max_fire_distance)
            self._board.spawn_missile((self._x, self._y), degree, distance, self._bullet_speed, self._bullet_damage,
                                      self)
            self._reloading = True
            self._reloading_counter = 0.0
            return True
        return False

    def distance(self, xy):
        if isinstance(xy, Robot):
            dist, angle = xy.distance((self._x, self._y))
            angle = (angle + 180) % 360
            return dist, angle
        dx = (xy[0] - self._x)
        dy = (xy[1] - self._y)
        dist = (dx ** 2 + dy ** 2) ** 0.5
        rads = atan2(dy, dx)
        # angle = (360 - degrees(rads)) % 360
        angle = degrees(rads) % 360
        return dist, angle

    def block(self):
        self._current_speed = 0
        self._required_speed = 0

    def tick(self, deltatime):
        # RELOADING
        if self._reloading:
            self._reloading_counter += deltatime
            if self._reloading_counter >= self._reloading_time:
                self._reloading = False
                self._reloading_counter = 0.0

        # SPEED calculation with accelleration/decelleration limit
        if self._current_speed <= self._required_speed:
            delta = accel = min(self._acceleration,
                                float(self._required_speed - self._current_speed) / float(deltatime))
        else:
            delta = decell = max(self._decelleration,
                                 float(self._required_speed - self._current_speed) / float(deltatime))

        # MOVEMENT
        movement = self._current_speed * deltatime + 0.5 * delta * deltatime ** 2
        dx = movement * cos(radians(self._heading))
        dy = movement * sin(radians(self._heading))
        self._x += dx
        self._y += dy

        # UPDATE velocity
        self._current_speed += delta * deltatime

        # COLLISION
        collision = self._board.detect_collision(self, (self._x, self._y), (dx, dy))
        if collision is not None:
            self.block()
            self._x, self._y = collision[:2]
            self.take_damage(collision[2])

    def take_damage(self, hp):
        self._hit_points -= hp
        if self._hit_points <= 0:
            self.block()
            self._hit_points = 0
            self._dead = True

    def get_name(self):
        return self._name

    def get_xy(self):
        return self._x, self._y

    def is_dead(self):
        return self._dead