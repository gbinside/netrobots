from math import atan2
from math import degrees
from rabbit import distance, urlopen
from urllib2 import HTTPError
from random import randint
import threading
import json

__author__ = 'roberto'


def goto(token, x, y):
    data = json.loads(urlopen('robot/' + token).read())
    dx = x - data['robot']['x']
    dy = y - data['robot']['y']
    heading = degrees(atan2(dy, dx))
    data = json.loads(urlopen('robot/' + token + '/drive', dict(degree=heading, speed=100), 'PUT').read())
    data = json.loads(urlopen('robot/' + token).read())
    # 80 break distance
    while distance(data['robot']['x'], data['robot']['y'], x, y) > 72.1 and data['robot']['speed'] > 0:  # breaking distance = approx 72.1 m
        data = json.loads(urlopen('robot/' + token).read())
    data = json.loads(urlopen('robot/' + token + '/drive', dict(degree=heading, speed=19), 'PUT').read())
    while data['robot']['speed'] > 20:
        data = json.loads(urlopen('robot/' + token).read())  # wait speed down

    return not data['robot']['dead']


def worker(token):
    try:
        while goto(token, randint(100, 900), randint(100, 900)):
            pass
    except HTTPError:
        pass


def main():
    data = json.loads(urlopen('robot/', {'name': 'SNIPERX'}, 'POST').read())
    token = data['token']
    print token
    t = threading.Thread(target=worker, args=(token,))
    t.start()

    data = json.loads(urlopen('robot/' + token).read())
    teta = 0
    resolution = 10
    while not data['robot']['dead']:
        data = json.loads(urlopen('robot/' + token + '/scan', {'degree': teta, 'resolution': resolution}, 'PUT').read())
        dist = data['distance']
        if dist > 0.1:  # maximum damage radius
            dist = max(41, dist)
            data = json.loads(urlopen('robot/' + token).read())
            if dist > 400:
                datad = json.loads(
                    urlopen('robot/' + token + '/scan', {'degree': teta + resolution / 2, 'resolution': resolution / 2},
                            'PUT').read())
                distance_2 = datad['distance']
                try:
                    json.loads(
                        urlopen('robot/' + token + '/cannon', {
                            'degree': teta + resolution / (2 if distance_2 > 0 else -2), 'distance': dist},
                            'PUT').read())
                except HTTPError:
                    continue
            else:
                try:
                    #print 'robot/' + token + '/cannon', {'degree': teta, 'distance': dist}, 'PUT'
                    json.loads(
                        urlopen('robot/' + token + '/cannon', {'degree': teta, 'distance': dist}, 'PUT').read())
                except HTTPError:
                    continue
        else:
            teta += resolution * 2
        data = json.loads(urlopen('robot/' + token).read())
    urlopen('robot/' + token, method='DELETE')


if __name__ == '__main__':
    while 1: main()