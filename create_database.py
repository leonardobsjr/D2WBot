# -*- coding: utf-8 -*-
from datetime import timedelta
from datetime import datetime

from tinydb import TinyDB
import pytz

from config import Config
import dotamatch
from dotamatch import MatchDetails
from dotamatch import MatchHistory
from dotamatch import PlayerSummaries
from dotamatch import Heroes

c = Config()
key = dotamatch.get_key()
match_history = MatchHistory(key)
match_details = MatchDetails(key)
account_details = PlayerSummaries(key)
heroes = Heroes(key).heroes()

def calculate_status(info):
    if info['win']:
        return "venceu"
    else:
        return "perdeu"

def utc_to_local(time):
    local_tz = pytz.timezone(c.timezone)
    local_dt = datetime.fromtimestamp(time, local_tz)
    if c.ignore_dst:
        return local_dt - local_dt.dst()
    else:
        return local_dt

def fill_match_info(match_details, account_id):
    player_stats = match_details.player(account_id)
    player_account_details = account_details.players(account_id).next()
    used_hero = heroes[player_stats["hero_id"]].localized_name
    radiant = player_stats["player_slot"] < 128  # unsigned 8-bit
    side = 'Radiant' if radiant else 'Dire'
    win = (match_details.radiant_win) == (side == 'Radiant')
    kills = player_stats['kills']
    deaths = player_stats['deaths']
    assists = player_stats['assists']
    gpm = player_stats['gold_per_min']
    last_hits = player_stats['last_hits']
    start_time = utc_to_local(match_details.utc_start_time).strftime(u'%d-%m-%Y às %H:%M:%S'.encode('utf-8'))
    duration = str(timedelta(seconds=match_details.duration))
    end_time = utc_to_local(match_details.utc_start_time + match_details.duration).strftime(
        u'%d-%m-%Y às %H:%M:%S'.encode('utf-8'))
    info = {'side': side, 'win': win, 'account_id': account_id, 'personaname': player_account_details.personaname,
            'hero': used_hero, 'match_id': match_details.match_id, 'kills': kills, 'deaths': deaths, 'assists': assists,
            'gpm': gpm, 'last_hits': last_hits, 'start_time': start_time, 'end_time': end_time,
            'duration': duration}
    return info

def create_message(info):
    #Ex: "NickName" [venceu/perdeu] de WindRanger em 01/01/1990 às 00:00:00 [Emoticon]. Duração da partida: 120m. KDA: 100/50/25
    default_single_message = u"\"{}\" {} de {} em {} {}. Duração da partida: {}. KDA: {}/{}/{}"

    #Ex: [Party Time [Emoticon]]! "NickName1 (Sven)" e "NickName2 (WindRanger)" [venceram/perderam] em 01/01/1990 às 00:00:00 [Emoticon]. Duração da partida: 120m. KDAs: 100/50/25, 0/50/100
    default_party_message = u"Party Time \U0001F389! {} {} em {} {}. Duração da partida: {}. KDAs: {}"

    #Ex: "Nickname1 (Sven) e Nickname2 (WindRanger) [ganharam/ganhou] de Nickname3 (Invoker) em 01/01/1990 às 00:00:00 [Emoticon]. Duração da partida: 120m. KDAs: 100/50/25, 0/50/100, 0/0/0
    default_versus_message = u"{} {} de {} em {} \U0001F4AA. Duração da partida: {}. KDAs: {}"

    end_time = info[0]['end_time'].decode('utf-8')
    duration = info[0]['duration']

    if len(info) == 1:
        info = info[0]
        # TODO: Create a way to randomize cool messages
        return default_single_message.format(info['personaname'],
                                         calculate_status(
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
                emoticon = u"\U0001F4AA"
            else:
                resultado = "perderam"
                emoticon = u"\U0001F629"

            message = default_party_message.format(party, resultado, end_time, emoticon, duration, kdas)
            return message
        else:
            winning_names_and_heroes = ["\"%s (%s)\"" % (i['personaname'], i['hero']) for i in info]
            losing_names_and_heroes = ["\"%s (%s)\"" % (i['personaname'], i['hero']) for i in info]
            kda_list = ["{}/{}/{}".format(i['kills'], i['deaths'], i['assists']) for i in winning_side+losing_side]
            resultado = ['ganharam' if len(winning_side)>1 else 'ganhou']
            message = default_versus_message.format(winning_names_and_heroes,resultado,losing_names_and_heroes,end_time,duration,kda_list)
            return message

#Database Config
db = TinyDB(c.db_path)
matches_table = db.table('matches')
matches_info_table = db.table('matches_info')
db.purge_tables()

for accountId in c.accounts:
    matches = match_history.matches(account_id=accountId, matches_requested=10, language="en_us")
    for m in matches:
        print "Creating registry for match %s, account %s"% (m.match_id,accountId)
        currentMatchDetails = match_details.match(m.match_id)
        matchInfo = fill_match_info(currentMatchDetails,accountId)
        matches_table.insert(
            {'account_id': accountId, 'match_id': m.match_id,
             'message': create_message([matchInfo]), 'date_added': str(datetime.now())}
        )
        matches_info_table.insert(matchInfo)
print "Fim!"