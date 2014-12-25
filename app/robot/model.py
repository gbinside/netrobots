from math import atan2, degrees, pi, sin, cos, radians
from random import randint
import json
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
        self._max_speed = 100
        self._acceleration = 40
        self._decelleration = -30
        self._max_sterling_speed = 50
        self._max_scan_distance = 700
        self._max_fire_distance = 700
        self._bullet_speed = 400
        """
        3%  --    A missile explodes within a 40 meter radius.
        5%  --    A missile explodes within a 20 meter radius.
        10% --    A missile explodes within a 5 meter radius.
        """
#        self._bullet_damage = ((40, 3), (20, 5), (5, 10))
        # changed to progessive damage
        self._bullet_damage = ((40, 3), (20, 2), (5, 5))
        self._reloading = False
        self._reloading_time = 2
        self._reloading_counter = 0
        self._max_actions = 1
        self._current_actions = 0
        if not app.app.config['TESTING']:
            self._x, self._y = randint(100, 900), randint(100, 900)

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
            degree, speed = int(degree) % 360, int(speed)
            if degree != self._heading and self._current_speed > self._max_sterling_speed:
                # overheat
                self.block()
            else:
                self._heading = degree
                self._required_speed = min(speed, self._max_speed)
            self._act_done()
            return True
        return None

    def _can_act(self):
        return self._current_actions < self._max_actions

    def _act_done(self):
        self._current_actions += 1

    def scan(self, degree, resolution):
        if self._can_act():
            degree, resolution = int(degree) % 360, max(1, int(resolution))
            distance = self._board.radar(self, (self._x, self._y), self._max_scan_distance, degree, resolution)
            self._act_done()
            return distance
        return None

    def cannon(self, degree, distance):
        if self._can_act():
            if self._reloading is False:
                degree, distance = int(degree) % 360, min(int(distance), self._max_fire_distance)
                self._board.spawn_missile((self._x, self._y), degree, distance, self._bullet_speed, self._bullet_damage)
                self._reloading = True
                self._act_done()
                return True
            return False
        return None

    def distance(self, xy):
        dx = (self._x - xy[0])
        dy = (self._y - xy[1])
        dist = (dx ** 2 + dy ** 2) ** 0.5
        rads = atan2(-dy, dx)
        rads %= 2 * pi
        angle = (360 - degrees(rads)) % 360
        return dist, angle

    def block(self):
        self._current_speed = 0
        self._required_speed = 0

    def endturn(self):
        self._current_actions = 0
        # REALOADING
        if self._reloading:
            self._reloading_counter += 1
            self._reloading_counter %= self._reloading_time
            if 0 == self._reloading_counter:
                self._reloading = False
        # SPEED calculation with accelleration/decelleration limit
        if self._current_speed <= self._required_speed:
            delta = accel = min(self._acceleration, self._required_speed - self._current_speed)
        else:
            delta = decell = max(self._decelleration, self._required_speed - self._current_speed)
        self._current_speed += delta
        # MOVEMENT
        dx = self._current_speed * cos(radians(self._heading))
        dy = self._current_speed * sin(radians(self._heading))
        self._x += dx
        self._y += dy
        # COLLISION
        collision = self._board.detect_collision(self, (self._x, self._y), (dx, dy))
        if collision is not None:
            self.block()
            self._x, self._y = collision[:2]
            self._hit_points -= collision[2]
        # Sync with other robots.
        self._board.join(self)
        return True

    def damage(self, hp):
        self._hit_points -= hp
        if self._hit_points<=0:
            self.block()
            self._hit_points = 0
            self._dead = True
