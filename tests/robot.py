from server.game_model import Robot
from server.game_model import Board
import unittest
import app

__author__ = 'roberto'


class RobotTestCase(unittest.TestCase):
    def setUp(self):
        app.app.config['TESTING'] = True

    def tearDown(self):
        pass

    def test_robot_init(self):
        board = Board()
        robot = Robot(board, 'GUNDAM')
        self.assertEqual(robot.get_status(),
                         {'name': 'GUNDAM', 'hp': 100, 'winner': False, 'dead': False, 'reloading': False,
                          'max_speed': 27, 'y': 500, 'x': 250, 'speed': 0, 'heading': 0})

    def test_acceleration(self):
        board = Board()
        robot = Robot(board, 'GUNDAM')
        robot.drive(0, 30)
        self.assertEqual(robot.get_status(),
                         {'name': 'GUNDAM', 'hp': 100, 'winner': False, 'dead': False, 'reloading': False,
                          'max_speed': 27, 'y': 500, 'x': 250, 'speed': 0, 'heading': 0})
        robot.tick(3)
        self.assertEqual(robot.get_status(),
                         {'name': 'GUNDAM', 'hp': 100, 'winner': False, 'dead': False, 'reloading': False,
                          'max_speed': 27, 'y': 500.0, 'x': 290.5, 'speed': 27, 'heading': 0})
        robot.tick(3)
        self.assertEqual(robot.get_status(),
                         {'name': 'GUNDAM', 'hp': 100, 'winner': False, 'dead': False, 'reloading': False,
                          'max_speed': 27, 'y': 500.0, 'x': 371.5, 'speed': 27, 'heading': 0})

    def test_acceleration_float(self):
        board = Board()
        robot = Robot(board, 'GUNDAM')
        robot.drive(0, 30)
        self.assertEqual(robot.get_status(),
                         {'name': 'GUNDAM', 'hp': 100, 'winner': False, 'dead': False, 'reloading': False,
                          'max_speed': 27, 'y': 500, 'x': 250, 'speed': 0, 'heading': 0})
        robot.tick(0.25)
        robot.tick(0.25)
        robot.tick(0.25)
        robot.tick(0.25)
        robot.tick(0.25)
        robot.tick(0.25)
        robot.tick(0.25)
        robot.tick(0.25)
        robot.tick(0.25)
        robot.tick(0.25)
        robot.tick(0.25)
        robot.tick(0.25)
        self.assertEqual(robot.get_status(),
                         {'name': 'GUNDAM', 'hp': 100, 'winner': False, 'dead': False, 'reloading': False,
                          'max_speed': 27, 'y': 500.0, 'x': 290.5, 'speed': 27, 'heading': 0})
        robot.tick(0.3333333333333333333333333333)
        robot.tick(0.3333333333333333333333333333)
        robot.tick(0.3333333333333333333333333333)
        robot.tick(1)
        robot.tick(1)
        self.assertEqual(robot.get_status(),
                         {'name': 'GUNDAM', 'hp': 100, 'winner': False, 'dead': False, 'reloading': False,
                          'max_speed': 27, 'y': 500.0, 'x': 371.5, 'speed': 27, 'heading': 0})

    def test_decelleration(self):
        board = Board()
        robot = Robot(board, 'GUNDAM')
        robot.drive(0, 30)
        self.assertEqual(robot.get_status(),
                         {'name': 'GUNDAM', 'hp': 100, 'winner': False, 'dead': False, 'reloading': False,
                          'max_speed': 27, 'y': 500, 'x': 250, 'speed': 0, 'heading': 0})
        robot.tick(3)
        self.assertEqual(robot.get_status(),
                         {'name': 'GUNDAM', 'hp': 100, 'winner': False, 'dead': False, 'reloading': False,
                          'max_speed': 27, 'y': 500.0, 'x': 290.5, 'speed': 27, 'heading': 0})
        robot.drive(0, 0)
        robot.tick(3)
        self.assertEqual(robot.get_status(),
                         {'name': 'GUNDAM', 'hp': 100, 'winner': False, 'dead': False, 'reloading': False,
                          'max_speed': 27, 'y': 500.0, 'x': 349.0, 'speed': 12, 'heading': 0})
        robot.tick(2.4)
        self.assertEqual(robot.get_status(),
                         {'name': 'GUNDAM', 'hp': 100, 'winner': False, 'dead': False, 'reloading': False,
                          'max_speed': 27, 'y': 500.0, 'x': 363.4, 'speed': 0.0, 'heading': 0})

    def test_cannon(self):
        board = Board()
        robot = Robot(board, 'GUNDAM')
        robot.cannon(0, 500)
        self.assertEqual(robot.get_status(),
                         {'name': 'GUNDAM', 'hp': 100, 'winner': False, 'dead': False, 'reloading': True,
                          'max_speed': 27, 'y': 500, 'x': 250, 'speed': 0, 'heading': 0})
        robot.tick(1)
        self.assertEqual(robot.get_status(),
                         {'name': 'GUNDAM', 'hp': 100, 'winner': False, 'dead': False, 'reloading': True,
                          'max_speed': 27, 'y': 500, 'x': 250, 'speed': 0, 'heading': 0})
        robot.tick(1)
        self.assertEqual(robot.get_status(),
                         {'name': 'GUNDAM', 'hp': 100, 'winner': False, 'dead': False, 'reloading': False,
                          'max_speed': 27, 'y': 500, 'x': 250, 'speed': 0, 'heading': 0})

    def test_scanner(self):
        board = Board()
        robot1 = Robot(board, 'GUNDAM1')
        robot2 = Robot(board, 'GUNDAM2', 1)

        self.assertEqual(robot1.scan(0, 10), 500)
        self.assertEqual(robot2.scan(180, 10), 500)

    def test_distance(self):
        board = Board()
        robot1 = Robot(board, 'GUNDAM1')

        self.assertEqual(robot1.distance((500, 500)), (250.0, 0.0))
        self.assertEqual(robot1.distance((250, 1000)), (500.0, 90.0))


if __name__ == '__main__':
    unittest.main()