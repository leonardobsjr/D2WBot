import os.path
from yowsup.common import YowConstants

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

#Yowsup Path Storage -
YOWSUP = ".yowsup"


# Profile Picture
# Status

# Whatsapp Credentials
class Config(object):
    def __init__(self):
        whatsapp_credentials_file = os.path.expanduser(WHATSAPP_CREDENTIALS)
        with open(whatsapp_credentials_file) as f:
            self.whatsapp_credentials = [line.rstrip('\n') for line in f.readlines()]
        self.accounts=[]
        with open(os.path.expanduser(ACCOUNTS)) as f:
                for i in f.readlines():
                    self.accounts.append(int(i.rstrip("\n")))
        self.groups = []
        with open(os.path.expanduser(GROUPS)) as f:
            for i in f.readlines():
                self.groups.append(i.rstrip("\n"))
        self.db_path = DB
        if not YOWSUP:
            YowConstants.PATH_STORAGE = YOWSUP

