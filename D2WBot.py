# -*- coding: utf-8 -*-

from datetime import datetime
from datetime import timedelta

from tinydb import TinyDB

from tinydb import where
import pytz

from dotamatch import *
import dotamatch




# Initializing the API
key = get_key()  # Steam Dev Key (~/.steamapi)
match_history = MatchHistory(key)
match_details = MatchDetails(key)
account_details = PlayerSummaries(key)

# Cached
heroes = Heroes(key).heroes()

# ActualDB
# Th3 Guyz
test = []
with open(os.path.expanduser("~/.testaccounts")) as f:
    for i in f.readlines():
        test.append(int(i.rstrip("\n")))

db = TinyDB('db.json')
db.purge()
db.purge_tables()
matches_table = db.table('matches')
matches_info_table = db.table('matches_info')


# TODO: Create a DECENT 'getStatus' function - Maybe with randomized messages based on the KDA?
# TODO: Make use of the fill_match_info return
def calculate_status(info):
    if info['win']:
        return "venceu"
    else:
        return "perdeu"


def create_message(info):
    # TODO: Create a way to randomize cool messages
    return u"\"{}\" {} de {} em {} que durou {}. KDA: {}/{}/{}".format(info['personaname'], calculate_status(info),
                                                                       info['hero'], info['end_time'].decode('utf-8'),
                                                                       info['duration'], info['kills'], info['deaths'],
                                                                       info['assists'])


# Converts to GMT -03:00
def utc_to_local(time):
    local_tz = pytz.timezone('Brazil/East')
    local_dt = datetime.fromtimestamp(time, local_tz)
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
            'hero': used_hero, 'gpm': gpm, 'last_hits': last_hits, 'start_time': start_time, 'end_time': end_time,
            'duration': duration}
    matches_info_table.insert(info)
    return info


def get_latest_matches():
    for accountId in test:
        # Returns a list of matches, even if we resquest only one
        currentMatch = match_history.matches(account_id=accountId, matches_requested=1, language="en_us")[0]
        currentMatchDetails = match_details.match(currentMatch.match_id)

        # Search if the match is already registered and retrieve generated message
        matches = matches_table.search(
            (where('account_id') == accountId) & (where('match_id') == currentMatch.match_id))
        if not matches:
            info = fill_match_info(currentMatchDetails, accountId)
            message = create_message(info)
            matches_table.insert(
                {'account_id': accountId, 'match_id': currentMatch.match_id, 'generated_message': message,
                 'date_added': str(datetime.now())})
            print message
        else:
            print matches[0]['generated_message']


def main():
    try:
        get_latest_matches()
        # print ""
    except dotamatch.api.ApiError:  # Não funciona por algum motivo
        print u"Erro ao conectar à API."


if __name__ == '__main__':
    main()
