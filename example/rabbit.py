import json
import sys
import threading
import time
import urllib
import urllib2
from math import atan2, degrees
from random import randint

__author__ = 'roberto'

BASE = 'http://127.0.0.1:8080/v1/'


def urlopen(url, data=None, method='GET'):
    content_header = {
        # 'Content-type': 'application/json',
        'Accept': 'application/vnd.error+json,application/json',
        'Accept-Version': '1.0'
    }
    if data:
        request = urllib2.Request(url=BASE + url, data=urllib.urlencode(data), headers=content_header)
    else:
        request = urllib2.Request(url=BASE + url, headers=content_header)
    request.get_method = lambda: method

    retry = 5
    wait_time = 0.1
    while retry:
        try:
            response = urllib2.urlopen(request)
            break
        except Exception as e:
            retry -= 1
            if not retry:
                exc_info = sys.exc_info()
                raise exc_info[1], None, exc_info[2]
            time.sleep(wait_time)
            wait_time *= 2.0
    return response


def distance(x0, y0, x1, y1):
    return ((x1 - x0) ** 2 + (y1 - y0) ** 2) ** 0.5


def goto(token, x, y):
    data = json.loads(urlopen('robot/' + token).read())
    dx = x - data['robot']['x']
    dy = y - data['robot']['y']
    heading = degrees(atan2(dy, dx))
    data = json.loads(urlopen('robot/' + token + '/drive', dict(degree=heading, speed=100), 'PUT').read())
    data = json.loads(urlopen('robot/' + token).read())
    # 80 break distance
    while distance(data['robot']['x'], data['robot']['y'], x, y) > 72.1 and data['robot'][
        'speed'] > 0:  # breaking distance = approx 72.1 m
        data = json.loads(urlopen('robot/' + token).read())
    data = json.loads(urlopen('robot/' + token + '/drive', dict(degree=heading, speed=0), 'PUT').read())
    while data['robot']['speed'] > 0:
        data = json.loads(urlopen('robot/' + token).read())  # wait speed down

    return not data['robot']['dead']


def delete(token):
    urlopen('robot/' + token, method='DELETE')


def main(argv):
    # create robot
    data = json.loads(urlopen('robot/',
                              {
                                  'name': argv[1] if len(argv) > 1 else 'RABBIT',
                                  'max_speed': 34,
                                  'max_fire_distance': 0,
                                  'max_scan_distance': 0
                              }, 'POST').read())
    # token is the signature to be used to send commands
    token = data['token']
    # main loop - goto random position
    try:
        while goto(token, randint(100, 900), randint(100, 900)):
            pass
    except:
        pass
    delete(token)


if __name__ == '__main__':
    try:
        n = int(sys.argv[1])
    except:
        main(sys.argv)
        sys.exit(0)
    pool = []
    for i in xrange(n):
        t = threading.Thread(target=main, args=([sys.argv[0], 'RABBIT{}'.format(i)],))
        t.start()
        pool.append(t)
    while 1:
        if False in [x.isAlive() for x in pool]:
            for i in xrange(len(pool)):
                pool[i] = threading.Thread(target=main, args=([sys.argv[0], 'RABBIT{}'.format(i)],))
                pool[i].start()
        time.sleep(1)
