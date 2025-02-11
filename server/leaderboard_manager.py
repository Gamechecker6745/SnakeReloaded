from leaderboard import Leaderboard
from utils import mode_to_string


class LeaderboardManager:
    def __init__(self, server):
        self.server = server

        # initialise leaderboards
        for game_type in range(0, 2):
            for game_mode in range(2, 4):
                Leaderboard(self, mode_to_string((game_type, game_mode)))

    def update(self):
        pass

    def append_to_leaderboard(self, score, name, mode):
        Leaderboard.instances[mode_to_string(mode)].appendToLeaderboard(score, name)

    def get_leaderboard_obj(self, mode):
        return Leaderboard.instances[mode_to_string(mode)]

    def print_leaderboard(self, mode):
        Leaderboard.instances[mode].text_print()

    def on_exit(self):
        Leaderboard.uploadData()
