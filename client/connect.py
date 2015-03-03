__author__ = 'Massimo Zaniboni'

from client.netrobots_pb2 import *
import zmq

class Connect:
    """Control Robot on a NetRobots GameServer.

    A robot can execute in one simulation pass these contemporary commands:
    - one scan command
    - one cannon fire command
    - one move command

    Each of these commands use a different device, so they can be used contemporary.

    All these commands are optionals.

    The API follow this philosophy:
    - scan, cannon, move commands are specified, but not sent immediately,
      because sending a command is a turn of the game, and it should done when all params are completed
    - the "wait" command send the scheduled commands, and wait for an answer from the server,
      and return the new board status.
    - if a robot has nothing to do, it must call repeatedly "wait", analyzing the status, this because
      the netrobots server expect that all robots send something,
      and because a robot should monitor the status
    - if a robot is too slow to sending a command, it loose a turn, the server will process
      only the commands of other robots, and the robot will continue doing the planned movements of previous commands
    """

    def __init__(self, game_server_address):

        self._game_server_address = game_server_address

        self._game_server_socket = zmq.Context.instance().socket(zmq.REQ)
        self._game_server_socket.connect(self._game_server_address)

        self._robot_token = None
        self._robot_command = None
        self.reset_request()

    def reset_request(self):
        """
        Schedule a do-nothing.
        """
        self._robot_command = RobotCommand()

    def get_game_server_socket(self):
        return self._game_server_socket

    def create_robot(self, creation_params):
        """
        Create immediately a robot, returning its status.

        :param creation_params: CreateRobot
        """

        self._name = creation_params.name

        c = MainCommand()
        c.createRobot.CopyFrom(creation_params)

        self.get_game_server_socket().send(c.SerializeToString())
        binary_status = self.get_game_server_socket().recv()

        self.reset_request()

        status = RobotStatus()
        status.ParseFromString(binary_status)

        self._robot_token = status.token

        return status

    def delete_robot(self):
        """
        Delete immediately a Robot on the server.
        """

        if self._robot_token is not None:
            c = MainCommand()
            c.deleteRobot.token = self._robot_token

            self.get_game_server_socket().send(c.SerializeToString())
            self.get_game_server_socket().recv()

        self.reset_request()

    def wait(self):
        """
        Send the scheduled robot commands to the server, and wait an answer, returning the new robot status.
        In case of an idle robot, it should call repeatedly this method.
        Repeated wait resend the previous scan and drive commands.
        Cannon fire command must be explicitely activated before calling wait.

        :return: RobotStatus
        """

        if self._robot_token is not None:
            c = MainCommand()
            c.robotCommand.CopyFrom(self._robot_command)
            c.robotCommand.token = self._robot_token

            self.get_game_server_socket().send(c.SerializeToString())

            status = RobotStatus()
            status.ParseFromString(self.get_game_server_socket().recv())
        else:
            status = None

        self._robot_command.ClearField('cannon')

        return status

    def drive(self, speed, direction):
        """
        Schedule a change motion of the robot.
        This command is only scheduled, and it must be sent explicitely with "wait" method.

        :param speed: int
        :param direction: int
        """

        v = Drive()
        v.speed = int(speed)
        v.direction = int(direction)
        self._robot_command.drive.CopyFrom(v)

    def scan(self, direction, semiaperture):
        """
        Schedule a scan.
        This command is only scheduled, and it must be sent explicitely with "wait" method.

        :param direction: int an angle
        :param semiaperture: int an angle
        """

        v = Scan()
        v.semiaperture = int(semiaperture) % 180
        v.direction = int(direction) % 360
        self._robot_command.scan.CopyFrom(v)

    def cannon(self, direction, distance):
        """
        Schedule a missile fire.
        This command is only scheduled, and it must be sent explicitely with "wait" method.

        :param direction: int an angle
        :param distance: int
        """

        v = Cannon()
        v.direction = int(direction) % 360
        v.distance = int(distance)
        self._robot_command.cannon.CopyFrom(v)

    def default_creation_params(self, robot_name):
        """
        To use during Robot creation, for setting params to default settings.

        :param robot_name: string
        """

        p = CreateRobot()
        p.name = robot_name
        p.maxHitPoints = -1
        p.maxSpeed = -1
        p.acceleration = -1
        p.decelleration = -1
        p.maxSterlingSpeed = -1
        p.maxScanDistance = -1
        p.maxFireDistance = -1
        p.bulletSpeed = -1
        p.bulletDamage = -1
        p.reloadingTime = -1

        return p

    def show_status(self, s):
        """
        Display the RobotStatus.

        :param s: RobotStatus
        """

        return show_status1(s)


def show_status1(s):
    """

    :param s: RobotStatus
    :return: string
    """
    r = "\n  name = " + s.name
    r = r + "\n  token = " + s.token
    r = r + "\n  globalTime = " + str(s.globalTime)
    r = r + "\n  hp = " + str(s.hp)
    r = r + "\n  direction = " + str(s.direction)
    r = r + "\n  speed = " + str(s.speed)
    r = r + "\n  x = " + str(s.x)
    r = r + "\n  y = " + str(s.y)
    r = r + "\n  dead = " + str(s.isDead)
    r = r + "\n  winner = " + str(s.isWinner)
    r = r + "\n  wellSpecifiedRobot = " + str(s.isWellSpecifiedRobot)
    r = r + "\n  maxSpeed = " + str(s.maxSpeed)
    r = r + "\n  reloading = " + str(s.isReloading)
    r = r + "\n  firedNewMissile = " + str(s.firedNewMissile)

    if s.HasField('scan'):
        r = r + "\n  scan.direction = " + str(s.scan.direction) + "\n  scan.semiaperture = " + str(
            s.scan.semiaperture) + "\n  scan.distance = " + str(s.scan.distance)

    return r
