__author__ = 'Massimo Zaniboni'

from server.netrobots_pb2 import *
import zmq

class Connect:
    """Create, and command a Robot on a GameServer.

    A robot can execute in one simulation pass these contemporary commands:
    - one scan command
    - one cannon fire command
    - one move command
    - one status command

    Each of these commands use a different device, so they can be used contemporary.

    """

    def __init__(self, game_server_address):

        self._game_server_address = game_server_address

        self._game_server_socket = zmq.Context.instance().socket(zmq.REQ)
        self._game_server_socket.connect(self._game_server_address)

        self._robot_token = None
        self._robot_command = None
        self.reset_request()

    def reset_request(self):
        self._robot_command = RobotCommand()

    def get_game_server_socket(self):
        return self._game_server_socket

    def create_robot(self, creation_params):
        """Create immediately a robot, returning its status."""

        self._name = creation_params.name

        c = MainCommand()
        c.createRobot.CopyFrom(creation_params)

        self.get_game_server_socket().send(c.SerializeToString())
        binary_status = self.get_game_server_socket().recv()

        self.reset_request()

        status = RobotStatus()
        status.ParseFromString(binary_status)

        self._token = status.token

        return status

    def delete_robot(self):
        """Delete immediately a Robot on the server."""

        if self._robot_token is not None:
            c = MainCommand()
            c.deleteRobot.token = self._robot_token

            self.get_game_server_socket().send(c.SerializeToString())
            self.get_game_server_socket().recv()

        self.reset_request()

    def send_robot_command(self):
        """Send the scheduled robot commands to the server, and wait an answer with the new robot status."""

        if self._robot_token is not None:
            c = MainCommand()
            c.robotCommand.token = self._robot_token
            c.robotCommand.CopyFrom(self._robot_command)

            self.get_game_server_socket().send(c.SerializeToString())

            status = RobotStatus()
            status.ParseFromString(self.get_game_server_socket().recv())
        else:
            status = None

        self.reset_request()

        return status

    def get_robot_status(self):
        """Ask immediately the robot status."""

        self.reset_request()
        return self.send_robot_command()

    def drive(self, speed, heading):
        """Schedule a change motion of the robot.
        This command is only scheduled, and it must be sent explicitely with send_robot_command."""

        v = Drive()
        v.speed = speed
        v.heading = heading
        self._robot_command.drive = v

    def scan(self, direction, semiaperture):
        """Schedule a scan.
        This command is only scheduled, and it must be sent explicitely with send_robot_command."""

        v = Scan()
        v.degree = semiaperture
        v.resolution = direction
        self._robot_command.scan = v

    def cannon(self, direction, distance):
        """Schedule a missile fire.
        This command is only scheduled, and it must be sent explicitely with send_robot_command."""

        v = Cannon()
        v.degree = direction
        v.distance = distance
        self._robot_command.cannon = v

    def default_robot_params(self, name):
        
        p = CreateRobot()
        p.name = name
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
        return show_status1(s)

def show_status1(s):
        r = "\n  name = " + s.name
        r = r + "\n  token = " + s.token
        r = r     + "\n  globalTime = " + str(s.globalTime)
        r = r     + "\n  hp = " + str(s.hp)
        r = r     + "\n  heading = " + str(s.heading)
        r = r     + "\n  speed = " + str(s.speed)
        r = r     + "\n  x = " + str(s.x)
        r = r     + "\n  y = " + str(s.y)
        r = r     + "\n  dead = " + str(s.dead)
        r = r     + "\n  winner = " + str(s.winner)
        r = r     + "\n  wellSpecifiedRobot = " + str(s.wellSpecifiedRobot)
        r = r     + "\n  maxSpeed = " + str(s.maxSpeed)
        r = r     + "\n  reloading = "  + str(s.reloading)
        r = r     + "\n  firedNewMissile = " + str(s.firedNewMissile)

        if s.HasField('scan'):
            r = r + "\n  scan.degree = " + str(s.scan.degree) + "\n  scan.resolution = " + str(s.scan.resolution) + "\n  scan.distance = " + str(s.scan.distance)

        return r
