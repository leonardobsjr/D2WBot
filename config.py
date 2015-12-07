# coding=utf-8

import os.path
import logging

# The file with the Whatsapp Credentials. Two lines, the first one is the login (phone number with country code)
# and the base64 encoded password
WHATSAPP_CREDENTIALS = "~/.wcredentials"

# Steam API developer key (http://steamcommunity.com/dev/apikey)
STEAM_KEY = "~/.steamapi"

# 32bits id. Accounts to be checked, one per line.
ACCOUNTS = "~/.accounts"

# Id of the groups that will receive the messages
GROUPS = "~/.groups"

# Database of matches
DB = "db.json"

# Time between checking (in minutes)
CHECKING_INTERVAL = 10

# Inform only the latest matches once or all last matches per account every CHECKING_INTERVAL
UNIQUE_MATCH_MESSAGE = True

# Message Timezone. Possible Timezones: pytz.all_timezones and http://en.wikipedia.org/wiki/List_of_tz_database_time_zones
TIMEZONE = 'Brazil/East'

# Date and Time format to be used in the messages
DATE_AND_TIME_FORMAT = u'%d-%m-%Y às %H:%M:%S'

# Ignore DST (Daylight Savings Time)
IGNORE_DST = True

# Include winning streak message?
WINNING_STREAK = True
WINNING_STREAK_FILE = "winning_streak_messages.pt_BR"

# Include losing streak message?
LOSING_STREAK = True
LOSING_STREAK_FILE = "losing_streak_messages.pt_BR"

# Logging settings
LOGGING_LEVEL = logging.INFO
LOGGING_FORMAT = '[%(levelname)s][%(asctime)s] %(message)s'
LOGGING_DATE_FORMAT = "%d-%m-%Y %H:%M:%S"

class Config(object):
    def __init__(self):
        whatsapp_credentials_file = os.path.expanduser(WHATSAPP_CREDENTIALS)
        self.whatsapp_credentials=[]
        with open(whatsapp_credentials_file) as f:
          for i in f.readlines():
            self.whatsapp_credentials.append(i.rstrip("\n"))
        self.accounts=[]
        with open(os.path.expanduser(ACCOUNTS)) as f:
                for i in f.readlines():
                    self.accounts.append(int(i.rstrip("\n")))
        self.groups = []
        with open(os.path.expanduser(GROUPS)) as f:
            for i in f.readlines():
                self.groups.append(i.rstrip("\n"))
        self.db_path = DB
        self.log_level = LOGGING_LEVEL
        self.log_format = LOGGING_FORMAT
        self.log_date_format = LOGGING_DATE_FORMAT
        self.checking_interval = CHECKING_INTERVAL
        self.unique_match_message = UNIQUE_MATCH_MESSAGE
        self.timezone = TIMEZONE
        self.date_and_time_format = DATE_AND_TIME_FORMAT
        self.ignore_dst = IGNORE_DST
        self.winning_streak = WINNING_STREAK
        self.winning_streak_file = WINNING_STREAK_FILE
        self.losing_streak = LOSING_STREAK
        self.losing_streak_file = LOSING_STREAK_FILE
