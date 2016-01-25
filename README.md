#Dota 2 Results WhatsApp Bot

This is a simple WhatsApp bot that messages contacts the latest matches played by a group of steam id's. The bot can also autodetect if there's two or more of the designated steam id's on a match, and make a proper message. 

The bot can be fully configured on the config.py. There's basically four files that needs to be set:

*WHATSAPP_CREDENTIALS* - Stores the WhatsApp Credentials in two lines, the first one being the login, the full number including the country code, and the second being the base64-encoded WhatsApp password, that can be obtained by a variety of methods. 
I recommend using the yowsup-cli application and use a dedicated WhatsApp account (number). 

*ACCOUNTS* - Stores the steam accounts to be checked. The account id is a 32bit. You can find it on the [SteamRep](http://steamrep.com) as the last numbers of the steam3ID.

*GROUPS* - Stores the contacts that will receive the messages. The group number can be found using the yowsup-cli, using the groups list option.

*STEAM_KEY* - Stores the Steam Dev Api key needed to fetch the matches from the Dota2 Web Api. You can get one on http://steamcommunity.com/dev/apikey.

Below there's some options that can be used to configure the bot, if you feel the need to.

*INSTANCE_NAME* - The name of this D2WBot instance. Needed to differentiate between multiple running bots.

*CHECKING_INTERVAL* - Time between checking (in minutes). The default value is 10. I don't recommend setting this to a very low value (like 1) because your steam dev key can be banned for abusing the Dota2 Api.

*UNIQUE_MATCH_MESSAGE* - Inform only the latest matches once or all last matches per account every CHECKING_INTERVAL. Default value is True. Make it False to deactivate.

*TIMEZONE* - This is the timezone that the times will be converted into. Possible Timezones: pytz.all_timezones and http://en.wikipedia.org/wiki/List_of_tz_database_time_zones.

*DATE_AND_TIME_FORMAT* - The format of the date. The default is the Brazilian one: days/months/years.

*IGNORE_DST* - Option to ignore DST (Daylight Savings Time). Making it False will make the bot check if DST os active and will make proper time adjustments.

*WINNING/LOSING_STREAK* - Activate the detection of, respectively, winning or losing streaks. The streaks starts on 3, but there's no upper limit.
The messages need to be put on *WINNING/LOSING_STREAK_FILE* on a CSV format. The streak messages don't show on party messages.

Errors do happen. In case of error, the bot will try to restart its normal function. You can configure this process quite a bit:

*NUMBER_OF_RETRIES* - Number of tries that the bot will try to restart and try to recover normal function. Default value is 10. 

*TIME_BETWEEN_RETRIES* - Time (in seconds) between each retry. It's advisable to not change this to a super-low value to give a change of the external error to get sorted out. Default value is 5 minutes.

And finally, there's the debug options:

*LOGGING_LEVEL* = Logging level of the running bot. Default value is INFO. Setting it as DEBUG will make a lot more messages appear and generated messages will not be sent trough WhatsApp, and will be written on the console instead.
*LOGGING_FORMAT* and *LOGGING_DATE_FORMAT* to set the format and the date of the log lines.

The D2WBot has BoxCar support. BoxCar is a free inbox for iPhone and Android. If this file is set, the bot will send a notification to your BoxCar inbox in case of a shutdown.

*BOXCAR_USER_CREDENTIALS_FILE* - The file with the user credentials of the boxcar user.

#Disclaimer

This piece of software is intended for personal use only. This project couldn’t exist without [WhatsApp](https://www.whatsapp.com/) and the [yowsup](https://github.com/tgalal/yowsup) project from [tgalal](https://github.com/tgalal), [Dota 2](http://www.dota2.com) and the [Dota 2 Wep Api](http://dev.dota2.com/showthread.php?t=47115). 

Special thanks to [veryhappythings](https://github.com/veryhappythings) for the [dotamatch](https://github.com/veryhappythings/dotamatch) project that provides the python bindings to the Dota 2 Web Api.

##License
This software  is licensed under the GPLv3+: http://www.gnu.org/licenses/gpl-3.0.html.

##Running the Bot

\> python D2WBot.py 

##To fix the SSH Errors:

sudo pip install --upgrade pyopenssl ndg-httpsclient pyasn1 pip

##About not-authorized errors

Check your login/password and then the version strings used on Yowsup. For more info, check: https://github.com/tgalal/yowsup/issues/1164
