import socket

from utils import recvMessage, generate_room_code, sendMessage, log
from room import Room


class Client:
    clients = []

    def __init__(self, server, connection, address):
        self.server = server
        self.connected = True
        self.connection: socket.socket = connection
        self.address = address

        self.room = None

        Client.clients.append(self)

        self.run()

    def run(self):
        while self.connected:
            message = recvMessage(self.connection)
            print("LOOP")

            match message[0]:
                case 0:  # disconnect
                    log(f'DISCONNECT', self.address[0])
                    self.disconnect(False)

                case 1:  # create room
                    log('ROOM CREATED')
                    self.create_room()

                case 2:  # join room
                    log('JOIN ROOM')
                    pass

                case 3:  # leave room
                    log('LEAVE ROOM')
                    self.leave_room()

                case 4:  # append to server leaderboard | message[1] = score, name, mode
                    log('UPDATE LEADERBOARD')
                    self.server.leaderboard_manager.append_to_leaderboard(*message[1])

                case 5:  # get server leaderboard | message[1] = mode
                    log('SEND LEADERBOARD')
                    sendMessage(self.connection, (5, (self.server.leaderboard_manager.get_leaderboard_obj(message[1]).data, message[1])))

        self.on_exit()

    def create_room(self):
        room_code = generate_room_code()
        Room(self.server, room_code, self)
        self.room = Room.rooms[room_code]
        sendMessage(self.connection, (1, room_code))

    def leave_room(self):
        self.room.players.remove(self)
        self.room = None

    def disconnect(self, server_disconnect):
        if server_disconnect:
            sendMessage(self.connection, (0,))

        if self.room is not None:
            self.room.players.remove(self)

        Client.clients.remove(self)

        self.connected = False

    def on_exit(self):
        self.connection.close()
