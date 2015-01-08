import json
from random import randint
from rabbit import goto, urlopen

__author__ = 'roberto'


def main():
    data = json.loads(urlopen('robot/', {'name': 'SNIPER'}, 'POST').read())
    token = data['token']
    goto(token, 500, 500)
    data = json.loads(urlopen('robot/' + token).read())
    teta = 0
    resolution = 10
    while not data['robot']['dead']:
        data = json.loads(urlopen('robot/' + token + '/scan', {'degree': teta, 'resolution': resolution}, 'PUT').read())
        if data['distance'] > 40:  # maximum damage radius
            data = json.loads(urlopen('robot/' + token).read())
            while data['robot']['reloading']:
                data = json.loads(urlopen('robot/' + token).read())
            json.loads(
                urlopen('robot/' + token + '/cannon', {'degree': teta, 'distance': data['distance']}, 'PUT').read())
        teta += resolution * 2
        data = json.loads(urlopen('robot/' + token).read())


if __name__ == '__main__':
    main()