import socket
from time import sleep
import threading
import pygame as pg
pg.init()


from client import Client
from room import Room
from leaderboard_manager import LeaderboardManager
from utils import log


class Server:
    def __init__(self):
        self.online = False
        self.ADDRESS = self.HOST, self.PORT = socket.gethostbyname(socket.gethostname()), 7070
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.T_accept_commands = threading.Thread(target=self.accept_commands, daemon=True)
        self.T_threaded_update = threading.Thread(target=self.threaded_update, daemon=True)

        self.listening = False

        # managers
        self.leaderboard_manager = LeaderboardManager(self)

    def accept_commands(self):
        while self.online:
            match input():
                case 'shutdown' | 'exit':
                    log('SHUTTING DOWN')
                    for client in Client.clients.copy():
                        try:
                            client.disconnect(True)
                        except ConnectionResetError:
                            pass

                    self.server.close()
                    self.online = False

                case 'leaderboard':
                    self.leaderboard_manager.print_leaderboard('02')

    def run(self):
        log("SERVER STARTING")

        self.server.bind(self.ADDRESS)
        self.online = True

        self.T_accept_commands.start()

        log(f"STARTED", f"Server running on {self.HOST}")

        self.server.listen()

        self.T_threaded_update.start()

        while self.online:
            self.update()

        self.on_exit()

    def threaded_update(self):
        while self.online:
            [room.update() for room in list(Room.rooms.values()).copy()]

    def update(self):
        self.manage_connections()

    def manage_connections(self):
        try:
            connection, address = self.server.accept()
            print("ACCEPT")
            threading.Thread(target=Client, args=(self, connection, address), daemon=True).start()
            log(f"CONNECTED", address[0])
        except OSError:
            pass

    def on_exit(self):
        self.leaderboard_manager.on_exit()
        sleep(1)


if __name__ == '__main__':
    server = Server()
    server.run()
