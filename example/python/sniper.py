"""Sniper positions itself in the center of the board and it starts scanning circularly and firing to targets."""

import json
from random import randint
from rabbit import goto, BASE

import sys
import os
lib_path = os.path.abspath(os.path.join('..', '..'))
sys.path.append(lib_path)
import client.connect as connect

__author__ = 'roberto'

def main():
    robot = connect.Connect(BASE)
    robot.create_robot(robot.default_creation_params("Sniper"))

    goto(robot, 500, 500)

    data = robot.wait()
    teta = 0
    resolution = 10
    while not data.isDead:
        robot.scan(teta, resolution)
        data = robot.wait()
        d = data.scan.distance

        if d > 40:  # maximum damage radius
            while data.isReloading:
                data = robot.wait()
            robot.cannon(teta, d)
            data = robot.wait()

        else:
            teta += resolution * 2

    robot.delete_robot()

if __name__ == '__main__':
    main()
