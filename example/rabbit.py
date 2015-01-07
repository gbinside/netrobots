from math import atan2, degrees
from random import randint
import urllib2
import urllib
import json
import sys

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
        request = urllib2.Request(url=BASE + url)
    request.get_method = lambda: method

    response = urllib2.urlopen(request)

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
    # 120 break distance
    while distance(data['robot']['x'], data['robot']['y'], x, y) > 120 * 1.5 and data['robot']['speed'] > 0:
        data = json.loads(urlopen('robot/' + token).read())
    data = json.loads(urlopen('robot/' + token + '/drive', dict(degree=heading, speed=0), 'PUT').read())
    while data['robot']['speed'] > 0:
        data = json.loads(urlopen('robot/' + token).read())  # wait speed down

    return not data['robot']['dead']


def main(argv):
    data = json.loads(urlopen('robot/', {'name': (argv[1] if len(argv) > 1 else 'RABBIT')}, 'POST').read())
    token = data['token']
    while goto(token, randint(100, 900), randint(100, 900)):
        pass


if __name__ == '__main__':
    main(sys.argv)