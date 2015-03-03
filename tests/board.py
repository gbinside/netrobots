from server.game_model import Robot
from server.game_model import Board
import unittest
import app

__author__ = 'roberto'


class BoardTestCase(unittest.TestCase):
    def setUp(self):
        app.app.config['TESTING'] = True

    def tearDown(self):
        pass

    def test_robot_collision(self):
        board = Board()
        robot1 = Robot(board, 'GUNDAM1')
        self.assertEqual(robot1.get_status(),
                         {'name': 'GUNDAM1', 'hp': 100, 'winner': False, 'dead': False, 'reloading': False,
                          'max_speed': 27, 'y': 500, 'x': 250, 'speed': 0, 'heading': 0})
        robot2 = Robot(board, 'GUNDAM2', 1)
        self.assertEqual(robot2.get_status(),
                         {'name': 'GUNDAM2', 'hp': 100, 'winner': False, 'dead': False, 'reloading': False,
                          'max_speed': 27, 'y': 500, 'x': 750, 'speed': 0, 'heading': 180})
        robot1.drive(0, 27)
        robot2.drive(180, 27)
        while robot1.get_status()['hp'] == 100:
            board.tick()
        status1 = robot1.get_status()
        status2 = robot2.get_status()
        self.assertEqual(status1['hp'], 98)
        self.assertEqual(status2['hp'], 98)
        self.assertAlmostEqual(status1['x'], 500, delta=2)
        self.assertAlmostEqual(status2['x'], 500, delta=2)
        self.assertEqual(robot1.distance(robot2), (2, 0))
        robot1.drive(180, 1)
        board.tick()
        self.assertEqual(robot1.distance(robot2), (2.0625, 0))

    def test_wall_collision(self):
        board = Board()
        robot1 = Robot(board, 'GUNDAM1')
        robot1.drive(45, 27)
        while robot1.get_status()['hp'] == 100:
            board.tick()
        self.assertAlmostEqual(robot1.get_xy()[0], 750)
        self.assertAlmostEqual(robot1.get_xy()[1], 1000)

        robot1.drive(-45, 27)
        while robot1.get_status()['hp'] == 98:
            board.tick()
        self.assertAlmostEqual(robot1.get_xy()[0], 1000)
        self.assertAlmostEqual(robot1.get_xy()[1], 750)

        robot1.drive(180 + 45, 27)
        while robot1.get_status()['hp'] == 96:
            board.tick()
        self.assertAlmostEqual(robot1.get_xy()[0], 250)
        self.assertAlmostEqual(robot1.get_xy()[1], 0)

        robot1.drive(180 - 45, 27)
        while robot1.get_status()['hp'] == 94:
            board.tick()
        self.assertAlmostEqual(robot1.get_xy()[0], 0)
        self.assertAlmostEqual(robot1.get_xy()[1], 250)

    def test_cannon(self):
        board = Board()
        robot1 = board.new_robot(Robot, 'GUNDAM1')
        robot2 = board.new_robot(Robot, 'GUNDAM2')

        robot1.cannon(0, 500)  # colpo pieno, full hit
        while len(board.get_status()['missiles']):
            board.tick()
        self.assertEqual(robot2.get_status()['hp'], 90)

        while robot1.get_status()['reloading']:
            board.tick()
        robot1.cannon(0, 490)  # mezzo colpo, half-hit
        while len(board.get_status()['missiles']):
            board.tick()
        self.assertEqual(robot2.get_status()['hp'], 85)

        while robot1.get_status()['reloading']:
            board.tick()
        robot1.cannon(0, 470)  # colpo di striscio, almost-hit
        while len(board.get_status()['missiles']):
            board.tick()
        self.assertEqual(robot2.get_status()['hp'], 82)


if __name__ == '__main__':
    unittest.main()