import threading
import time
import zmq
import zmq.error
from game_model import *
from netrobots_pb2 import *
import json
from client.connect  import show_status1

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

        client_socket = zmq.Context.instance().socket(zmq.REQ)
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
        self.processed_robots = {}
        self.init_game()

    def init_game(self):
        self._board = Board()
        self.pending_robot_command_to_process = None
        self.processed_robots = {}

    def run(self):

        wake_up_socket =  zmq.Context.instance().socket(zmq.REP)
        wake_up_socket.bind(self._wake_up_socket_name)

        client_socket = zmq.Context.instance().socket(zmq.REP)

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
        # Initialize status variables, to use during processing of requests
        self.processed_robots = {}

        # Update the board
        self._board.tick(self._deltatime)

        # Update the robots according the requests from clients.
        again = True
        while again:
            binary_command = None
            try:
                if self.pending_robot_command_to_process is not None:
                    robot_command = self.pending_robot_command_to_process
                    self.pending_robot_command_to_process = None
                    self.process_robot_request(robot_command)
                else:
                    binary_command = client_socket.recv(zmq.NOBLOCK)
                    command = MainCommand()
                    command.ParseFromString(binary_command)

                    if command.HasField('createRobot'):
                        self.process_create_robot_request(command.createRobot, client_socket)

                    elif command.HasField('deleteRobot'):
                        self.process_delete_robot_request(command.deleteRobot)

                    elif command.HasField('robotCommand'):
                        can_be_processed = self.process_robot_request(command.robotCommand, client_socket)
                        if can_be_processed:
                            again = True
                            self.pending_robot_command_to_process = None
                        else:
                            again = False
                            self.pending_robot_command_to_process = command.robotCommand
                            # This robot can not be processed immediately, because this is an event related
                            # to the next simulation tick. So pause, waiting all other requests are sent to this server,
                            # and then resume starting from this robot.
                            # NOTE: this algo work because ZMQ assure that messages are retrieved from queues using a
                            # round-robin algorithm, so before processing the messages of the same robot/client,
                            # all the messages of other robots are processed.

            except zmq.error.Again:
                # there are no more messages to process in the queue
                self.pending_robot_command_to_process = None
                again = False

            except:
                # there is an error processing the command for this client.
                if binary_command is not None:
                    client_socket.send(b"")
                    # in ZMQ is mandatory sending an answer

    def process_create_robot_request(self, request, client_socket):
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

        client_socket.send(status.SerializeToString())

    def process_delete_robot_request(self, request):
        self._board.remove_robot_by_token(request.token)

    def process_robot_request(self, request, client_socket):
        """Process only new robots. Otherwise return False.
        Use implicitely also the status initializated from process_robots_requests."""

        if request.token in self.processed_robots:
            return False
        else:
            self.processed_robots[request.token]

        robot = self._board.get_robot_by_token(request.token)
        if robot is None:
            raise NameError('Unknown Robot')

        assert isinstance(robot, Robot)

        if self._board.global_time < robot.last_command_executed_at_global_time:
            raise NameError('Client is sending too much requests')

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

        client_socket.send(robot.get_status().SerializeToString())

        return True
