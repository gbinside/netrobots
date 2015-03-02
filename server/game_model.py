__author__ = 'Roberto'

import hashlib
from math import cos, sin, radians, atan2, degrees, pi
from random import randint
import time
from netrobots_pb2 import *


class Board:
    def __init__(self, size=(1000, 1000)):
        self._global_time = 0
        self._size = size
        self.robots = {}
        self.robots_by_token = {}
        self._missiles = {}
        self._explosions = {}
        self._radar = {}
        self._wall_hit_damage = 2
        self._join_status = None
        self.kdr = {}

    def global_time(self):
        return self._global_time


    def create_robot(self, original_name, configurations):
        """Create a new robot with some configurations. Return an inactive status in case of problems. """

        name = original_name
        c = 2
        while name in self.robots:
            name = original_name + "_" + c
            c = c + 1
        # @ensure name is a unique name inside the system

        _new_robot = Robot(name, len(self.robots), configuration=configurations, is_testing=False)
        if _new_robot.calc_value() > 327:
            _new_robot._dead = True
            _new_robot._well_specified_robot = False
            _new_robot._token = ''
        else:
            self.add_robot(_new_robot)

        return _new_robot.get_status()


    def add_robot(self, robot):
        """Add the robot inside the board."""
        if robot.get_name() not in self.robots:
            self.robots[robot.get_name()] = robot
            self.robots_by_token[robot.get_token()] = robot
            robot.last_command_executed_at_global_time = self.global_time()
            return True
        return False

    def remove_robot(self, robot):
        if robot.get_name() in self.robots:
            del self.robots[robot.get_name()]
            del self.robots_by_token[robot.get_token()]
            return True
        return False

    def remove_robot_by_token(self, token):
        if token in self.robots_by_token:
            robot = self.robots_by_token[token]
            return self.remove_robot(robot)
        else:
            return False

    def get_robot_by_token(self, token):
        return self.robots_by_token[token]

    def reinit(self, size=(1000, 1000)):
        self.__init__(size)

    def get_status(self):
        ret = dict(
            size=self._size,
            robots=[v.get_status() for v in self.robots.values()],
            missiles=dict([(k, v.get_status()) for k, v in self._missiles.items()]),
            explosions=dict([(k, v.get_status()) for k, v in self._explosions.items()]),
            radar=dict(self._radar),
            kdr=self.kdr,
            global_time=self._global_time
        )
        self._radar = dict([(k, v) for k, v in self._radar.items() if v['spawntime'] + 1.0 > time.time()])
        return ret

    def radar(self, scanning_robot, xy, max_scan_distance, degree, resolution):
        key = hashlib.md5(repr(dict(time=time.time(), xy=xy, degree=degree, resolution=resolution,
                                    distance=max_scan_distance))).hexdigest()
        self._radar[key] = dict(xy=xy, degree=degree, resolution=resolution, distance=max_scan_distance,
                                spawntime=time.time())
        ret = []
        degree %= 360
        for robot in [x for x in self.robots.values() if x != scanning_robot]:
            if robot.is_dead():
                continue
            distance, angle = robot.distance(xy)
            angle = (180 + angle) % 360
            if self.angle_distance(angle, degree) > resolution:
                continue
            if distance > max_scan_distance:
                continue
            ret.append(distance)
        return min(ret) if ret else 0

    def detect_collision(self, robot, xy, dxy):
        x, y = xy
        dx, dy = dxy
        # collision with other robots
        step = max(abs(dx), abs(dy))
        if step:  # the robot is moving
            x0, y0 = x - dx, y - dy
            stepx = float(dx) / float(step)
            stepy = float(dy) / float(step)
            for other_robot in [j for j in self.robots.values() if j != robot]:
                xp, yp = x0, y0
                for i in xrange(int(step) + 1):
                    dist, angle = other_robot.distance((xp, yp))
                    if dist < 2:  # 1 per ogni robot
                        other_robot.take_damage(self._wall_hit_damage)
                        other_robot.block()
                        teta = atan2(dy, dx)
                        xp, yp = other_robot.get_xy()
                        xp -= 2 * cos(teta)
                        yp -= 2 * sin(teta)
                        return xp, yp, self._wall_hit_damage
                    xp += stepx
                    yp += stepy
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
        return None

    def spawn_missile(self, xy, degree, distance, bullet_speed, bullet_damage, owner=None):
        key = hashlib.md5(repr(
            dict(time=time.time(), xy=xy, degree=degree, distance=distance, bullet_speed=bullet_speed,
                 bullet_damage=bullet_damage))).hexdigest()
        missile = Missile(self, xy, degree, distance, bullet_speed, bullet_damage, owner)
        self._missiles[key] = missile

    def remove_missile(self, missile):
        self._missiles = dict([(k, x) for k, x in self._missiles.items() if x != missile])
        # del self._missiles[self._missiles.index(missile)]

    def spawn_explosion(self, xy, damage, owner=None):
        key = hashlib.md5(repr(dict(time=time.time(), xy=xy, damage=damage))).hexdigest()
        self._explosions[key] = Explosion(self, xy, damage, owner)

    def remove_explosion(self, explosion):
        self._explosions = dict([(k, x) for k, x in self._explosions.items() if x != explosion])

    def tick(self, deltatime=0.125):
        self._global_time = self._global_time + deltatime

        # manage missiles
        for m in self._missiles.values():
            assert isinstance(m, Missile)
            m.tick(deltatime)
        # manage explosions
        for e in self._explosions.values():
            assert isinstance(e, Explosion)
            e.tick(deltatime)
        # manage robots
        for r in self.robots.values():
            r.tick(deltatime)

    def new_robot(self, clazz, name):
        return clazz(self, name, len(self.robots))

    @staticmethod
    def angle_distance(angle, degree):
        ret = (angle - degree) if angle > degree else (degree - angle)
        if ret > 180:
            ret = 360 - ret
        return ret


class Missile:
    def __init__(self, board, xy, degree, distance, speed, damage, owner=None):
        assert isinstance(board, Board)
        self._board = board
        self._owner = owner
        self._x, self._y = xy
        self._degree = degree
        self._distance = distance
        self._speed = speed
        self._damage = damage
        self._space = 0.0

    def tick(self, deltatime):
        dx = self._speed * cos(radians(self._degree)) * deltatime
        dy = self._speed * sin(radians(self._degree)) * deltatime
        self._distance -= self._speed * deltatime
        if self._distance < 1:
            self._board.spawn_explosion((self._x + dx + self._distance * cos(radians(self._degree)),
                                         self._y + dy + self._distance * sin(radians(self._degree))),
                                        self._damage,
                                        self._owner)
            self._board.remove_missile(self)
        self._x += dx
        self._y += dy

    def get_status(self):
        return dict(
            x=self._x,
            y=self._y,
            degree=self._degree,
            distance=self._distance,
            speed=self._speed,
            damage=self._damage
        )


class Explosion:
    def __init__(self, board, xy, damage, owner=None):
        assert isinstance(board, Board)
        self._owner = owner
        self._board = board
        self._x, self._y = xy
        self._damage = damage
        self._step = 0
        self._explosion_time = 1.0  # sec

    def tick(self, deltatime):
        self._step += 1
        if 1 == self._step:
            # do damage
            for robot in self._board.robots.values():
                d, a = robot.distance((self._x, self._y))
                total_damage = 0
                for distance, hp_damage in self._damage:
                    if d <= distance:
                        total_damage += hp_damage
                if total_damage:
                    robot.take_damage(total_damage)
                    if robot.is_dead():
                        if robot.get_name() not in self._board.kdr:
                            self._board.kdr[robot.get_name()] = {'kill': 0, 'death': 0}
                        self._board.kdr[robot.get_name()]['death'] += 1
                        if self._owner and self._owner.get_name() not in self._board.kdr:
                            self._board.kdr[self._owner.get_name()] = {'kill': 0, 'death': 0}
                        self._board.kdr[self._owner.get_name()]['kill'] += 1
        elif self._step > 1:
            self._explosion_time -= deltatime
            if self._explosion_time <= 0.0:
                self._board.remove_explosion(self)

    def get_status(self):
        return dict(
            x=self._x,
            y=self._y,
            step=self._step,
            damage=self._damage,
            time=self._explosion_time
        )


class RobotAlreadyExistsException(Exception):
    pass


START_COORDS = [(250, 500), (750, 500), (500, 250), (500, 750), (250, 250), (750, 750), (750, 250), (250, 750)]
START_HEADING = [0, 180, 90, 270, 45, 225, 135, 315]


class Robot:
    def __init__(self, name, count_of_other, configuration=None, is_testing=False):

        self._token = hashlib.md5(name + time.strftime('%c')).hexdigest()

        self.scan_degree = None
        self.scan_resolution = None
        self.scan_distance = None
        self.fired_new_missile = False

        self.last_command_executed_at_global_time = -1

        self._name = name
        self._max_hit_points = 100
        self._hit_points = self._max_hit_points
        self._winner = False
        self._dead = False
        self._well_specified_robot = True
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

        for k, v in configuration.items():
            if not (v == -1):
                if hasattr(self, '_' + k):
                    setattr(self, '_' + k, v)

        if not is_testing:
            self._x, self._y = randint(100, 900), randint(100, 900)

    def get_token(self):
        return self._token

    def calc_value(self):
        return sum([
            self._max_hit_points,
            2 * self._max_speed,
            2 * self._acceleration,
            -2 * self._decelleration,
            2 * self._max_sterling_speed,
            0.01 * self._max_scan_distance,
            0.01 * self._max_fire_distance,
            0.01 * self._bullet_speed,
            0.005 * pi * sum([(x[0] ** 2) * x[1] for x in self._bullet_damage]),
            10 * (3 - self._reloading_time),
        ])

    def get_data(self):
        return dict(
            name=self._name,
            max_hit_points=self._max_hit_points,
            required_speed=self._required_speed,
            max_speed=self._max_speed,
            acceleration=self._acceleration,
            decelleration=self._decelleration,
            max_sterling_speed=self._max_sterling_speed,
            max_scan_distance=self._max_scan_distance,
            max_fire_distance=self._max_fire_distance,
            bullet_speed=self._bullet_speed,
            bullet_damage=self._bullet_damage,
            reloading_time=self._reloading_time,
            reloading_counter=self._reloading_counter,
            fired_new_missile=self.fired_new_missile
        )

    def get_status(self):
        r = RobotStatus()

        r.name = self._name
        r.token = self.get_token()
        r.globalTime = self.last_command_executed_at_global_time
        r.hp = self._hit_points
        r.heading = self._heading
        r.speed = self._current_speed
        r.x = self._x
        r.y = self._y
        r.dead = self._dead
        r.wellSpecifiedRobot = self._well_specified_robot
        r.winner = self._winner
        r.max_speed = self._max_speed
        r.reloading = self._reloading
        r.firedNewMissile = self.fired_new_missile

        if self.scan_degree is not None:
            r.scan.degree = self.scan_degree
            r.scan.resolution = self.scan_resolution
            r.scan.distance = self.scan_distance

        return r

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

        self.scan_degree = degree
        self.scan_resolution = resolution
        self.scan_distance = distance

        return True

    def no_scan(self):
        self.scan_degree = None
        self.scan_resolution = None
        self.scan_distance = None

        return True

    def cannon(self, degree, distance):
        if self.is_dead():
            self.fired_new_missile = False
            return False
        if self._reloading is False:
            degree, distance = int(float(degree)) % 360, min(int(float(distance)), self._max_fire_distance)
            self._board.spawn_missile((self._x, self._y), degree, distance, self._bullet_speed, self._bullet_damage,
                                      self)
            self._reloading = True
            self._reloading_counter = 0.0

            self.fired_new_missile = True
            return True

        self.fired_new_missile = False
        return False

    def no_cannon(self):
        self.fired_new_missile = False

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

