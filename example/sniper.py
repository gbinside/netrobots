import json
from random import randint
from rabbit import goto, urlopen

__author__ = 'roberto'


def main():
    data = json.loads(urlopen('robot/', {'name': 'SNIPER'}, 'POST').read())
    token = data['token']
    while not data['robot']['dead']:
        data = goto(token, 50 if randint(0, 1) else 950, 50 if randint(0, 1) else 950)
        if not data['robot']['dead']:
            pass

if __name__ == '__main__':
    main()