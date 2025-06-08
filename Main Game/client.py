import socket
import threading
import pickle
import struct
from time import sleep

from leaderboard import Leaderboard
from utils import mode_to_string


LENGTH_BYTE = 16
WAIT_MAX_TIME = 3


class Client:
    def __init__(self, app):
        self.app = app
        self.online = False

        self.ADDRESS = self.HOST, self.PORT = socket.gethostbyname(socket.gethostname()), 7070  # "192.168.0.12", 7070
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self._sending = False
        self.attempting_connection = False
        self._time_since_last_send = 0

        self.in_room = False
        self.room_code = None

    def attempt_connection(self):
        self.attempting_connection = True

        try:
            self.client.connect(self.ADDRESS)
            self._time_since_last_send = 0
            self.online = True
        except (ConnectionRefusedError, TimeoutError):
            self.online = False

        self.attempting_connection = False

    def connect_to_server(self):
        threading.Thread(target=self.attempt_connection, daemon=True).start()
        threading.Thread(target=self.listen, daemon=True).start()
        threading.Thread(target=Leaderboard.update_server, daemon=True).start()

    def sendMessage(self, message):
        self._sending = True
        packet = pickle.dumps(message)
        length = struct.pack('!I', len(packet))
        packet = length + packet
        self.client.send(packet)
        self._time_since_last_send = 0
        self._sending = False

    def threadedSend(self, message):
        threading.Thread(target=self.sendMessage, args=(message,), daemon=True).start()

    def recvMessage(self):
        buf = b''
        while len(buf) < 4:
            buf += self.client.recv(4 - len(buf))

        length = struct.unpack('!I', buf)[0]

        rawMessage = self.client.recv(length)
        msg = pickle.loads(rawMessage)
        return msg

    def listen(self):
        while self.attempting_connection:
            pass
        while self.online:
            try:
                msg = self.recvMessage()  # msg[0] = instruction msg[1] = arguments

                match msg[0]:
                    case 0:  # server shutdown
                        self.disconnect()
                    case 1:  # room code
                        self.room_code = msg[1]
                    case 5:
                        self.app.global_leaderboards[mode_to_string(msg[1][1])] = Leaderboard(self.app, mode_to_string(msg[1][1]), msg[1][0], add_to_class=False, load_data=False)
            except EOFError:
                pass

    def create_room(self):
        self.threadedSend((1,))
        self.in_room = True

    def leave_room(self):
        self.threadedSend((3,))
        self.in_room = False

    def update(self):
        self._time_since_last_send += self.app.delta_time

    def append_to_global_leaderboard(self, score, name, mode):
        if self.online:
            self.threadedSend((4, (score, name, mode)))

    def get_global_leaderboard(self, mode):
        if self.online:
            self.threadedSend((5, mode))

    def disconnect(self):
        self.online = False
        self.in_room = False
        self.room_code = None
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def on_exit(self):
        if self.online:
            self.threadedSend((0,))

        while self._sending:
            self.update()

        self.disconnect()
