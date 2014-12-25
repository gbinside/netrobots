from math import cos, sin, radians
import time
import app

class Missile:
    def __init__(self, board, xy, degree, distance, speed, damage):
        assert isinstance(board, Board)
        self._board = board
        self._x, self._y = xy
        self._degree = degree
        self._distance = distance
        self._speed = speed
        self._damage = damage

    def tick(self):
        dx = min(self._speed, self._distance) * cos(radians(self._degree))
        dy = min(self._speed, self._distance) * sin(radians(self._degree))
        self._distance -= min(self._speed, self._distance)
        self._x += dx
        self._y += dy
        if self._distance < 1:
            self._board.spawn_explosion((self._x, self._y), self._damage)

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

    def tick(self):
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
                    robot.damage(total_damage)
        elif 2 == self._step:
            # delete self
            self._board.remove_missile(self)

    def get_status(self):
        return dict(
            x=self._x,
            y=self._y,
            step=self._step,
            damage=self._damage
        )


class Board:
    def __init__(self, size=(1000, 1000)):
        self._size = size
        self.robots = {}
        self._missiles = []
        self._explosions = []
        self._wall_hit_damage = 2
        self._join_status = None

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
                for i in xrange(int(step)+1):
                    dist, angle = other_robot.distance((xp, yp))
                    if dist < 2:  # 1 per ogni robot
                        other_robot.damage(self._wall_hit_damage)
                        other_robot.block()
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
        del self._explosions[self._explosions.index(explosion)]

    def join(self, robot):
        if not app.app.config['TESTING']:
            time.sleep(1)
        if self._join_status is None:
            self._join_status = len(self.robots)
        self._join_status -= 1
        if 0 == self._join_status:
            self._join_status = None
            self.end_turn()
        return True

    def end_turn(self):
        # manage missiles
        for m in self._missiles:
            assert isinstance(m, Missile)
            m.tick()
        # manage explosions
        for e in self._explosions:
            assert isinstance(e, Explosion)
            e.tick()
        # manage robots
        for r in self.robots.values():
            r.tick()