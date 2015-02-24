import json
from random import randint
from rabbit import goto, urlopen
import time

__author__ = 'luca'


def main():
    data = json.loads(urlopen('robot/', {'name': 'BURSTER'}, 'POST').read())
    token = data['token']
    data = json.loads(urlopen('robot/' + token).read())
    teta = 0
    resolution = 10
    while not data['robot']['dead']:
        # can i scan?
        if data['robot']['scanning'] is False:
            data = json.loads(urlopen('robot/' + token + '/scan', {'degree': teta, 'resolution': resolution}, 'PUT').read())
            distance = data['distance']
            if distance > 40:  # maximum damage radius
                data = json.loads(urlopen('robot/' + token).read())
                if not data['robot']['bursting']:
                    burst = {'degree_start': teta, 'distance_start': distance, 'degree_end': teta+resolution*2, 'distance_end': distance}
                    data = json.loads(urlopen('robot/' + token + '/burst', burst , 'PUT').read())
            else:
                teta += resolution * 2
        data = json.loads(urlopen('robot/' + token).read())
    urlopen('robot/'+token, method='DELETE')

if __name__ == '__main__':
    main()