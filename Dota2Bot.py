# -*- coding: utf-8 -*-

import threading
import time
import pytz

import dotamatch
from dotamatch import MatchHistory
from dotamatch import MatchDetails
from dotamatch import Heroes
from dotamatch import PlayerSummaries

from config import Config
from datetime import datetime
from datetime import timedelta

from tinydb import TinyDB
from tinydb import where

class D2WBot(object):
    def __init__(self):
        self.sentCache = {}
        self.checkingThread = threading.Thread(target = self.startThread)
        self.checkingThread.daemon = True
        self.config = Config()

        # Debug purposes
        self.printOutput = False

        # Initializing the API
        key = dotamatch.get_key()  # Steam Dev Key (~/.steamapi)
        try:
            self.match_history = MatchHistory(key)
            self.match_details = MatchDetails(key)
            self.account_details = PlayerSummaries(key)
            self.heroes = Heroes(key).heroes()

            # ActualDB
            db = TinyDB(self.config.db_path)
            #db.purge()
            #db.purge_tables()

            self.matches_table = db.table('matches')
            self.matches_info_table = db.table('matches_info')
        except dotamatch.api.ApiError:
            print u"Erro ao conectar à API."

    def startChecking(self):
        self.checkingThread.start()

    def startThread(self):
        while True:
            if not self.connected:
                self.L() # Quick Connect
                timer = 0
                while(not self.connected):
                    time.sleep(1) # Waiting a connection to establish
                    timer += 1
                    if timer == 10:
                        timer = 0
                        self.L()
            print "["+str(datetime.now().time())+"] Getting matches..."
            messages = self.get_latest_matches()
            for m in messages:
                self.message_send(self.config.groups[0],m.encode('utf-8'))
            self.disconnect()
            time.sleep(10*60) # Wait 10 minutes and check again!

    def getPrompt(self):
        return "[%s]:" % ("connected" if self.connected else "offline")

    def printPrompt(self):
        # return "Enter Message or command: (/%s)" % ", /".join(self.commandMappings)
        print(self.getPrompt())

    def output(self, message, tag="general", prompt=True):
        if self.printOutput:
            print(message)
        else:
            pass

    # TODO: Create a DECENT 'getStatus' function - Maybe with randomized messages based on the KDA?
    # TODO: Make use of the fill_match_info return
    def calculate_status(self,info):
        if info['win']:
            return "venceu"
        else:
            return "perdeu"

    def create_message(self,info):
        # TODO: Create a way to randomize cool messages
        return u"\"{}\" {} de {} em {} que durou {}. KDA: {}/{}/{}".format(info['personaname'], self.calculate_status(info),
                                                                           info['hero'], info['end_time'].decode('utf-8'),
                                                                           info['duration'], info['kills'], info['deaths'],
                                                                           info['assists'])

    # Converts to GMT -03:00
    def utc_to_local(self,time):
        local_tz = pytz.timezone('Brazil/East')
        local_dt = datetime.fromtimestamp(time, local_tz)
        return local_dt

    def fill_match_info(self,match_details, account_id):
        player_stats = match_details.player(account_id)
        player_account_details = self.account_details.players(account_id).next()
        used_hero = self.heroes[player_stats["hero_id"]].localized_name
        radiant = player_stats["player_slot"] < 128  # unsigned 8-bit
        side = 'Radiant' if radiant else 'Dire'
        win = (match_details.radiant_win) == (side == 'Radiant')
        kills = player_stats['kills']
        deaths = player_stats['deaths']
        assists = player_stats['assists']
        gpm = player_stats['gold_per_min']
        last_hits = player_stats['last_hits']
        start_time = self.utc_to_local(match_details.utc_start_time).strftime(u'%d-%m-%Y às %H:%M:%S'.encode('utf-8'))
        duration = str(timedelta(seconds=match_details.duration))
        end_time = self.utc_to_local(match_details.utc_start_time + match_details.duration).strftime(
            u'%d-%m-%Y às %H:%M:%S'.encode('utf-8'))
        info = {'side': side, 'win': win, 'account_id': account_id, 'personaname': player_account_details.personaname,
                'hero': used_hero, 'match_id': match_details.match_id, 'kills': kills, 'deaths': deaths, 'assists': assists,
                'hero': used_hero, 'gpm': gpm, 'last_hits': last_hits, 'start_time': start_time, 'end_time': end_time,
                'duration': duration}
        self.matches_info_table.insert(info)
        return info

    def get_latest_matches(self):
        messages = []
        for accountId in self.config.accounts:
            # Returns a list of matches, even if we resquest only one
            currentMatch = self.match_history.matches(account_id=accountId, matches_requested=1, language="en_us")[0]
            currentMatchDetails = self.match_details.match(currentMatch.match_id)

            # Search if the match is already registered and retrieve generated message
            matches = self.matches_table.search(
                (where('account_id') == accountId) & (where('match_id') == currentMatch.match_id))
            if not matches:
                info = self.fill_match_info(currentMatchDetails, accountId)
                message = self.create_message(info)
                self.matches_table.insert(
                    {'account_id': accountId, 'match_id': currentMatch.match_id, 'generated_message': message,
                     'date_added': str(datetime.now())})
                messages.append(message)
            else:
                messages.append(matches[0]['generated_message'])
        return messages
