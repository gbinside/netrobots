"""Test the connection."""

import sys
import os
lib_path = os.path.abspath(os.path.join('..', '..'))
sys.path.append(lib_path)

from math import atan2, degrees
from random import randint
import sys
import client.connect as connect

__author__ = 'roberto'

BASE = 'tcp://127.0.0.1:5555'

def main(argv):
    robot = connect.Connect(BASE)
    status = robot.create_robot(robot.default_creation_params("Test"))

    if status.isWellSpecifiedRobot:

        robot.drive(25, 50)
        data = robot.wait()
        c = 1
        while not data.isDead:
            c = c + 1
            if c % 20 == 0:
                robot.cannon(90, 200)
                data = robot.wait()
                print "\n c = " + str(c) + ", " + robot.show_status(data)
            else:
                data = robot.wait()

if __name__ == '__main__':
    main(sys.argv)
