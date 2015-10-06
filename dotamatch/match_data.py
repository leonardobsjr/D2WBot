__author__ = 'leonardo'


class MatchData:
    def __init__(self, steam_id, hero, win, start_time, end_time, kills, deaths, assists):
        self.steam_id = steam_id
        self.hero = hero
        self.win = win
        self.start_time = start_time
        self.end_time = end_time
        self.kills = kills
        self.deaths = deaths
        self.assists = assists

    def format_kda(self):
        return self.kills + "/" + self.deaths + "/" + self.assists
