#Dota 2 Results Whatsapp Bot

This is a simple bot that messages whatsapp contacts the latest matches played by a group of steam id's. The bot can be 
fully configured on the config.py. There's basically four files that needs to be set:

*wcredentials* - Stores the WhatsApp Credentials in two lines, the first one being the login, the full number including the country code, and the second being the base64-encoded WhatsApp password, that can be obtained by a variety of methods. 
I recommend using the yowsup-cli application and use a dedicated WhatsApp account (number). 

*accounts* - Stores the steam accounts to be checked. The account id is a 32bit. You can find it on the [SteamRep](http://steamrep.com) as the last numbers of the steam3ID.

*groups* - Stores the contacts that will receive the messages. The group number can be found using the yowsup-cli, using the groups list option.

*steamapi* - Stores the Steam Dev Api key needed to fetch the matches from the Dota2 Web Api. You can get one on http://steamcommunity.com/dev/apikey.

##Running the Bot

\> python D2WBot.py 

##To fix the SSH Errors:

sudo pip install --upgrade pyopenssl ndg-httpsclient pyasn1 pip

