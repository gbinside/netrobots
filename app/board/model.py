from math import cos, sin, radians, atan2
import threading
import time


class BoardThread(threading.Thread):
    def __init__(self, tick, deltatime, sleep_time=None):
        threading.Thread.__init__(self)
        self._tick = tick
        self._deltatime = deltatime
        self._sleep_time = sleep_time if sleep_time is not None else deltatime

    def run(self):
        while 1:
            self._tick(self._deltatime)
            time.sleep(self._sleep_time)

    def get_sleep_time(self):
        return self._sleep_time


class Missile:
    def __init__(self, board, xy, degree, distance, speed, damage):
        assert isinstance(board, Board)
        self._board = board
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
                                         self._y + dy + self._distance * sin(radians(self._degree))), self._damage)
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
    def __init__(self, board, xy, damage):
        assert isinstance(board, Board)
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
        elif self._step > 1:
            self._explosion_time -= deltatime
            if self._explosion_time <= 0.0:
                self._board.remove_explosion(self)

    def get_status(self):
        return dict(
            x=self._x,
            y=self._y,
            step=self._step,
            damage=self._damage
        )


class RobotAlreadyExistsException(Exception):
    pass


class Board:
    def __init__(self, size=(1000, 1000)):
        self._size = size
        self.robots = {}
        self._missiles = []
        self._explosions = []
        self._wall_hit_damage = 2
        self._join_status = None

    def add_robot(self, robot):
        if robot.get_name() not in self.robots:
            self.robots[robot.get_name()] = robot
            return True
        return False

    def reinit(self, size=(1000, 1000)):
        self.__init__(size)

    def get_status(self):
        return dict(
            size=self._size,
            robots=[v.get_status() for v in self.robots.values()],
            missiles=[x.get_status() for x in self._missiles],
            explosions=[x.get_status() for x in self._explosions],
        )

    def radar(self, scanning_robot, xy, max_scan_distance, degree, resolution):
        ret = []
        for robot in [x for x in self.robots.values() if x != scanning_robot]:
            distance, angle = robot.distance(xy)
            angle = (180 + angle) % 360
            if angle > degree + resolution or angle < degree - resolution:
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

    def spawn_missile(self, xy, degree, distance, bullet_speed, bullet_damage):
        missile = Missile(self, xy, degree, distance, bullet_speed, bullet_damage)
        self._missiles.append(missile)

    def remove_missile(self, missile):
        self._missiles = [x for x in self._missiles if x != missile]
        # del self._missiles[self._missiles.index(missile)]

    def spawn_explosion(self, xy, damage):
        self._explosions.append(Explosion(self, xy, damage))

    def remove_explosion(self, explosion):
        self._explosions = [x for x in self._explosions if x != explosion]

    def tick(self, deltatime=0.125):
        # manage missiles
        for m in self._missiles:
            assert isinstance(m, Missile)
            m.tick(deltatime)
        # manage explosions
        for e in self._explosions:
            assert isinstance(e, Explosion)
            e.tick(deltatime)
        # manage robots
        for r in self.robots.values():
            r.tick(deltatime)

    def new_robot(self, clazz, name):
        return clazz(self, name, len(self.robots))
