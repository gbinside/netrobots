import threading
import time
import zmq
import zmq.error
from game_model import *
from client.netrobots_pb2 import *
import json

COMMAND_WAKE_UP = b"tick"
COMMAND_RESET_GAME = b"reset-game"
COMMAND_GET_BOARD = b"get-board"

class WakeUpThread(threading.Thread):
    """Advise the GameThread that it must update the game."""

    def __init__(self, sleep_time, wake_up_socket_name, client_socket_name):
        """Sleep time are the seconds on which the server is suspended waiting requests from the clients.
        It should be enough for each client, for sending its request, without loosing a turn."""

        threading.Thread.__init__(self)
        self._sleep_time = sleep_time

        self._wake_up_socket_name = wake_up_socket_name
        self._client_socket_name = client_socket_name

    def run(self):
        wake_up_socket = zmq.Context.instance().socket(zmq.REQ)
        wake_up_socket.connect(self._wake_up_socket_name)

        client_socket = zmq.Context.instance().socket(zmq.ROUTER)
        client_socket.connect(self._client_socket_name)

        while 1:
            wake_up_socket.send(COMMAND_WAKE_UP)
            wake_up_socket.recv()

            next_wake_time = time.clock() + self._sleep_time
            next_pause = next_wake_time - time.clock()
            if next_pause > 0:
                time.sleep(next_pause)


class GameThread(threading.Thread):
    """Update the Game Status."""

    def __init__(self, deltatime, wake_up_socket_name, client_socket_name):
        threading.Thread.__init__(self)
        self._deltatime = deltatime
        self._wake_up_socket_name = wake_up_socket_name
        self._client_socket_name = client_socket_name
        self._board = Board()
        self.pending_robot_command_to_process = None

        self.processed_robots = None
        self.banned_robots = None
        self.queued_robot_messages = None
        self.init_game()

    def init_game(self):
        self._board = Board()
        self.pending_robot_command_to_process = None

        self.processed_robots = {}
        self.banned_robots = {}
        self.queued_robot_messages = {}

    def run(self):

        wake_up_socket =  zmq.Context.instance().socket(zmq.REP)
        wake_up_socket.bind(self._wake_up_socket_name)

        client_socket = zmq.Context.instance().socket(zmq.ROUTER)

        client_socket.bind(self._client_socket_name)

        while True:
            message = wake_up_socket.recv()

            if message == COMMAND_WAKE_UP:
                self.process_robots_requests(client_socket)
                wake_up_socket.send(b"")
            elif message == COMMAND_RESET_GAME:
                self.init_game()
                wake_up_socket.send(b"")
            elif message == COMMAND_GET_BOARD:
                wake_up_socket.send(json.dumps(self._board.get_status()))
            else:
                assert(False)

    def process_robots_requests(self, client_socket):

        self._board.tick(self._deltatime)

        self.processed_robots = self.queued_robot_messages
        # for sure a queued robot, can not send process commands in this turn

        # First process queued robots.
        for token, v in self.queued_robot_messages.iteritems():
            try:
                self.process_robot_command(v['sender_address'], v['command'], client_socket)
            except:
                client_socket.send_multipart([v['sender_address'], b'', b''])
                # in ZMQ is mandatory sending an answer

        self.queued_robot_messages = {}

        # Update the robots according the new requests from clients.
        again = True
        while again:
            sender_address = None
            try:
                sender_address, empty, binary_command = client_socket.recv_multipart(zmq.NOBLOCK)
                command = MainCommand()
                command.ParseFromString(binary_command)
                self.process_robot_command(sender_address, command, client_socket)

            except zmq.error.Again:
                # there are no more messages to process in the queue
                again = False

            except:
                # there is an error processing the command for this client.
                if sender_address is not None:
                    client_socket.send_multipart([sender_address, b'', b''])
                    # in ZMQ is mandatory sending an answer

    def process_robot_command(self, sender_address, command, client_socket):
        if command.HasField('createRobot'):
            self.process_create_robot_request(command.createRobot, sender_address, client_socket)

        elif command.HasField('deleteRobot'):
            self.process_delete_robot_request(command.deleteRobot, sender_address, client_socket)

        elif command.HasField('robotCommand'):
            token = command.robotCommand.token

            if token in self.banned_robots:
                # nothing to do, avoid to answer to these requests
                if token in self.queued_robot_messages:
                    self.banned_robots[token] = True
                else:
                    if token in self.processed_robots:
                        self.queued_robot_messages[token] = {'sender_address': sender_address, 'command': command }
                    else:
                        self.processed_robots[token] = True
                        self.process_robot_request(sender_address, command.robotCommand, client_socket)

    def process_create_robot_request(self, sender_address, request, client_socket):
        """Create a Robot. If the Robot does not respect the constraints it is returned dead,
         and with wellSpecifiedRobot = False"""

        assert(isinstance(request, CreateRobot))

        extra = dict(
            max_hit_points=request.maxHitPoints,
            max_speed=request.maxSpeed,
            acceleration=request.acceleration,
            decelleration=request.decelleration,
            max_sterling_speed=request.maxSterlingSpeed,
            max_scan_distance=request.maxScanDistance,
            max_fire_distance=request.maxFireDistance,
            bullet_speed=request.bulletSpeed,
            bullet_damage=request.bulletDamage,
            reloading_time=request.reloading_Time
        )

        status = self._board.create_robot(request.name, configuration=extra)
        client_socket.send_multipart([sender_address, b'', status.SerializeToString()])

    def process_delete_robot_request(self, sender_address, request, client_socket):
        self._board.remove_robot_by_token(request.token)
        client_socket.send_multipart([sender_address, b'', b''])

    def process_robot_request(self, sender_address, request, client_socket):

        robot = self._board.get_robot_by_token(request.token)
        if robot is None:
            raise NameError('Unknown Robot')

        assert isinstance(robot, Robot)

        robot.last_command_executed_at_global_time = self._board.global_time

        if request.HasField('scan'):
            robot.scan(request.scan.degree, request.scan.resolution)
        else:
            robot.no_scan()

        if request.HasField('cannon'):
            robot.cannon(request.cannon.degree, request.cannon.distance)
        else:
            robot.no_cannon()

        if request.HasField('drive'):
            robot.drive(request.drive.degree, request.drive.speed)

        client_socket.send_multipart([sender_address, b'', robot.get_status().SerializeToString()])
