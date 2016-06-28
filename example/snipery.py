from math import degrees, radians, sin, cos, atan2
from rabbit import distance, urlopen
from urllib2 import HTTPError
from random import randint
from time import sleep
import threading
import json
import sys

__author__ = 'roberto'

robot = {}
robot_extra = {}


def angle_distance(angle, degree):
    ret = (angle - degree) if angle > degree else (degree - angle)
    if ret > 180:
        ret = 360 - ret
    return ret


def get_status(token):
    global robot
    try:
        data = json.loads(urlopen('robot/' + token).read())
        robot = data['robot']
    except HTTPError:
        pass


def statuser(token):
    while 1:
        get_status(token)


def slowdown(token):
    json.loads(urlopen('robot/' + token + '/drive', dict(degree=robot['heading'], speed=10), 'PUT').read())
    while robot['speed'] > 12:
        sleep(0.01)


def goto(token):
    px = robot_extra['desidered_x']
    py = robot_extra['desidered_y']
    heading = degrees(atan2(py - robot['y'], px - robot['x']))
    if angle_distance(robot['heading'], heading) > 5 and robot['speed'] > 12:
        slowdown(token)
        heading = degrees(atan2(py - robot['y'], px - robot['x']))
    # cambio rotta
    json.loads(urlopen('robot/' + token + '/drive', dict(degree=heading, speed=100), 'PUT').read())
    # 80 break distance
    while distance(robot['x'], robot['y'], px, py) > 72.1 and \
                    robot['speed'] > 0 and \
                    px == robot_extra['desidered_x'] and py == robot_extra['desidered_y']:
        sleep(0.01)
    if distance(robot['x'], robot['y'], px, py) <= 72.1 and \
            px == robot_extra['desidered_x'] and \
            py == robot_extra['desidered_y']:
        robot_extra['desidered_x'] = randint(100, 900)
        robot_extra['desidered_y'] = randint(100, 900)


def driver(token):
    robot_extra['desidered_x'] = randint(100, 900)
    robot_extra['desidered_y'] = randint(100, 900)
    try:
        while 1:
            goto(token)
    except HTTPError:
        pass


def scan(teta, resolution, token):
    data = json.loads(urlopen('robot/' + token + '/scan', {'degree': teta, 'resolution': resolution}, 'PUT').read())
    dist = data['distance']
    if dist > 0.1:  # maximum damage radius
        dist = max(41, dist)
        # data = json.loads(urlopen('robot/' + token).read())
        if dist > 400:
            datad = json.loads(
                urlopen('robot/' + token + '/scan', {'degree': teta + resolution / 2, 'resolution': resolution / 2},
                        'PUT').read())
            distance_2 = datad['distance']
            if distance_2 > 0.1:
                return robot['x'] + cos(radians(teta + resolution / 2)) * distance_2, robot['y'] + sin(
                    radians(teta)) * distance_2
            else:
                return robot['x'] + cos(radians(teta - resolution / 2)) * dist, robot['y'] + sin(radians(teta)) * dist
        else:
            return robot['x'] + cos(radians(teta)) * dist, robot['y'] + sin(radians(teta)) * dist
    else:
        return None


def cannon(scan_xy, token):
    try:
        urlopen('robot/' + token + '/cannon', {
            'degree': degrees(atan2(scan_xy[1] - robot['y'], scan_xy[0] - robot['x'])),
            'distance': distance(robot['x'], robot['y'], scan_xy[0], scan_xy[1])},
                'PUT').read()
    except HTTPError:
        pass


def delete(token):
    urlopen('robot/' + token, method='DELETE')


def main():
    data = json.loads(urlopen('robot/', {'name': 'SNIPERY' if len(sys.argv)<2 else sys.argv[1], 'bullet_damage': json.dumps(((23, 10),))}, 'POST').read())
    token = data['token']
    print token

    get_status(token)
    t1 = threading.Thread(target=statuser, args=(token,))
    t1.setDaemon(True)
    t1.start()

    t2 = threading.Thread(target=driver, args=(token,))
    t2.setDaemon(True)
    t2.start()

    teta = 0
    resolution = 10
    while not robot['dead']:
        scan_xy = scan(teta, resolution, token)
        if scan_xy is not None:
            cannon(scan_xy, token)
            robot_extra['desidered_x'], robot_extra['desidered_y'] = scan_xy
        else:
            teta += resolution * 1.9
    delete(token)


if __name__ == '__main__':
    while 1:
        main()
