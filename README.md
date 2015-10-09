#Dota 2 Results Whatsapp Bot

This is a simple bot that messages whatsapp contacts the latest matches of a group of steam id's. The bot can be fully configured on the config.py. There's basically four files that needs to be set:

*wcredentials* - Stores the Whatsapp Credentials in two lines, the first one being the login, the full number including the country code, and the second being the base64-encoded whatsapp password, that can be obtained by a variety of methods. I recommend using the yowsup-cli application.

*accounts* - Stores the steam accounts to be checked.

*groups* - Stores the contacts that will receive the messages.

#To fix the SSH Errors:

sudo pip install --upgrade pyopenssl ndg-httpsclient pyasn1 pip

> Written with [StackEdit](https://stackedit.io/).