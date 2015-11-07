# -*- coding: utf-8 -*-

import threading
import time
from datetime import datetime
from datetime import timedelta
import logging

import pytz
from tinydb import TinyDB
from tinydb import where

import dotamatch
from dotamatch import MatchHistory
from dotamatch import MatchDetails
from dotamatch import Heroes
from dotamatch import PlayerSummaries
from config import Config


class D2WBot_Utils(object):
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
            # hdb.purge_tables()

            self.matches_table = db.table('matches')
            self.matches_info_table = db.table('matches_info')
        except dotamatch.api.ApiError:
            print u"Erro ao conectar à API."

    def startChecking(self):
        self.checkingThread.start()

    def startThread(self):
        while True:
            try:
                # Doesn't connect on debug
                if not self.connected and self.config.log_level == logging.INFO:
                    self.L() # Quick Connect
                    timer = 0
                    while(not self.connected):
                        time.sleep(1) # Waiting a connection to establish
                        timer += 1
                        if timer == 10:
                            timer = 0
                            self.L()
                logging.info("Fetching matches...")
                latest_matches = self.find_latest_matches()
                messages = self.generate_messages(latest_matches)
                if messages:
                    logging.info("Found %s new matches!"%len(messages))
                    for m in messages:
                        if self.config.log_level == logging.DEBUG:
                            print(m)
                        else:
                            self.message_send(self.config.groups[0], m.encode('utf-8'))
                if self.connected:
                    self.disconnect()
            except dotamatch.api.ApiError:
                logging.error("The Dota2 Api is Down, can't fetch matches.")
            except Exception, e:
                logging.error("Because of an unknown error, i couldn't fetch matches. Exception: %s"%e.__class__,exc_info=True)

            logging.info("Cicle complete, sleeping for %s minutes ..."%self.config.checking_interval)
            time.sleep(self.config.checking_interval*60) # Wait and check again l3ter.

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
        #Ex: "NickName" [venceu/perdeu] de WindRanger em 01/01/1990 às 00:00:00 [Emoticon]. Duração da partida: 120m. KDA: 100/50/25
        default_single_message = u"\"{}\" {} de {} em {} {}. Duração da partida: {}. KDA: {}/{}/{}"

        #Ex: [Party Time [Emoticon]]! "NickName1 (Sven)" e "NickName2 (WindRanger)" [venceram/perderam] em 01/01/1990 às 00:00:00 [Emoticon]. Duração da partida: 120m. KDAs: 100/50/25, 0/50/100
        default_party_message = u"Party Time \U0001F389! {} {} em {}. Duração da partida: {}. KDAs: {}"

        #Ex: "Nickname1 (Sven) e Nickname2 (WindRanger) [ganharam/ganhou] de Nickname3 (Invoker) em 01/01/1990 às 00:00:00 [Emoticon]. Duração da partida: 120m. KDAs: 100/50/25, 0/50/100, 0/0/0
        default_versus_message = u"{} {} de {} em {} \U0001F4AA. Duração da partida: {}. KDAs: {}"

        end_time = info[0]['end_time'].decode('utf-8')
        duration = info[0]['duration']

        if len(info) == 1:
            info = info[0]
            # TODO: Create a way to randomize cool messages
            return default_single_message.format(info['personaname'],
                                             self.calculate_status(
                                                 info),
                                             info['hero'],
                                             end_time,
                                             (u"\U0001F44F" if info[
                                                 'win'] else u"\U0001F622"),
                                             duration,
                                             info['kills'],
                                             info['deaths'],
                                             info['assists'])
        else:
            winning_side = [i for i in info if i['win']]
            losing_side = [i for i in info if not i['win']]
            same_sides = len(winning_side) == 0 or len(losing_side) == 0

            # TODO: Check if they're in a party
            if same_sides:
                # The message created is a party message, but in reality it doesn't check if they're in a party
                names_and_heroes = ["\"%s (%s)\"" % (i['personaname'], i['hero']) for i in info]
                kda_list = ["{}/{}/{}".format(i['kills'], i['deaths'], i['assists']) for i in info]

                party = " e ".join([", ".join(names_and_heroes[:-1]), names_and_heroes[-1]])
                kdas = ", ".join(kda_list)

                if info[0]['win']:
                    resultado = "venceram"
                else:
                    resultado = "perderam"
                message = default_party_message.format(party, resultado, end_time, duration, kdas)
                return message
            else:
                winning_names_and_heroes = ["\"%s (%s)\"" % (i['personaname'], i['hero']) for i in info]
                losing_names_and_heroes = ["\"%s (%s)\"" % (i['personaname'], i['hero']) for i in info]
                kda_list = ["{}/{}/{}".format(i['kills'], i['deaths'], i['assists']) for i in winning_side+losing_side]
                resultado = ['ganharam' if len(winning_side)>1 else 'ganhou']
                message = default_versus_message.format(winning_names_and_heroes,resultado,losing_names_and_heroes,end_time,duration,kda_list)
                return message

    # Converts the UTC time of the match to the current set timezone in config.py
    def utc_to_local(self,time):
        local_tz = pytz.timezone(self.config.timezone)
        local_dt = datetime.fromtimestamp(time, local_tz)
        if self.config.ignore_dst:
            return local_dt - local_dt.dst()
        else:
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
                'gpm': gpm, 'last_hits': last_hits, 'start_time': start_time, 'end_time': end_time,
                'duration': duration}
        self.matches_info_table.insert(info)
        return info

    # Find the latest matches (1 per AccountID)
    def find_latest_matches(self):
        matches = {}
        for accountId in self.config.accounts:
            # Returns a list of matches, even if we resquest only one
            currentMatch = self.match_history.matches(account_id=accountId, matches_requested=1, language="en_us")[0]
            currentMatchDetails = self.match_details.match(currentMatch.match_id)

            # Find if there's two players in the same match
            if not matches.get(currentMatch.match_id, False):
                matches[currentMatch.match_id] = currentMatch, currentMatchDetails, [accountId]
            else:
                matches[currentMatch.match_id][2].append(accountId)
        return matches

    def generate_messages(self, matches):
        messages = []
        for match_id, match_information in matches.iteritems():
            currentMatch = match_information[0]
            currentMatchDetails = match_information[1]
            accounts = match_information[2]
            match_player_info = []
            matches_to_insert = []
            for accountId in accounts:
                # If the match is registered already, don't register again
                db_matches = self.matches_table.search(
                    (where('account_id') == accounts[0]) & (where('match_id') == currentMatch.match_id))
                if not db_matches:
                    match_player_info.append(self.fill_match_info(currentMatchDetails, accountId))
                    matches_to_insert.append(
                        {'account_id': accountId, 'match_id': currentMatch.match_id,
                         'date_added': str(datetime.now())}
                    )
                elif not self.config.unique_match_message:
                    messages.append(db_matches[0]['generated_message'])

            # If there's matches to process...
            if match_player_info:
                message = self.create_message(match_player_info)
                messages.append(message)
                for mpi in match_player_info:
                    for mti in matches_to_insert:
                        if mti['account_id'] == mpi['account_id']:
                            mti['generated_message'] = message
                            self.matches_table.insert(mti)

        # Removing duplicate messages due to the party detection
        return set(messages)

    @DeprecationWarning
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
            elif not self.config.unique_match_message:
                messages.append(matches[0]['generated_message'])
        return messages
