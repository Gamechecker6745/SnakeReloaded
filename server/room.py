class Room:
    rooms = {}

    ROOM_LIMIT = 2

    def __init__(self, server, code, host):
        self.server = server
        self.players: list = [host]
        self.code = code

        Room.rooms[self.code] = self

    def update(self):
        if not self.players:
            print(f'[ROOM DELETED]')
            Room.rooms.pop(self.code)
            del self

    def is_waiting(self):
        return len(self.players) < Room.ROOM_LIMIT
