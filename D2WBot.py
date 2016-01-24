import sys
import logging
import time
import json
import urllib2
import urllib

from yowsup.stacks import YowStackBuilder
from yowsup.layers.auth import AuthError
from yowsup.layers import YowLayerEvent
from yowsup.env import S40YowsupEnv

from config import Config
from botLayer import BotLayer


class D2WBot(object):
    # Create the Yowsup stack
    def __init__(self, credentials, encryptionEnabled=False):
        stackBuilder = YowStackBuilder()
        self.stack = stackBuilder \
            .pushDefaultLayers(encryptionEnabled) \
            .push(BotLayer) \
            .build()

        self.stack.setCredentials(credentials)

    def start(self):
        self.stack.broadcastEvent(YowLayerEvent(BotLayer.EVENT_START))
        try:
            self.stack.loop(timeout=0.5, discrete=0.5)
        except AuthError as au:
            self.stack.broadcastEvent(YowLayerEvent(BotLayer.EVENT_SHUTDOWN))
            raise au
        except KeyboardInterrupt:
            logging.info("D2WBot signing out!")
            sys.exit(0)
        except Exception as ex:
            self.stack.broadcastEvent(YowLayerEvent(BotLayer.EVENT_SHUTDOWN))
            raise ex

def checkNewVersion(currentVersion, currentAuth):
    currSettings = json.load(urllib2.urlopen("https://coderus.openrepos.net/whitesoft/whatsapp_scratch"))
    return currentVersion!=currSettings['e'] or currentAuth!=currSettings['b'][:-7]

if __name__ == "__main__":
    c = Config()  # Load the configurations
    # GTFO Urllib3 logger
    urllib3_logger = logging.getLogger('urllib3')
    urllib3_logger.setLevel(logging.CRITICAL)
    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.basicConfig(stream=sys.stdout, level=c.log_level, format=c.log_format, datefmt=c.log_date_format)
    remaining_shutdown_tries = c.number_of_retries # Retries till shutdown
    while remaining_shutdown_tries > 0:
        s = D2WBot(c.whatsapp_credentials, False)
        s.__setattr__("config", c)  # Make config accessible to the stack
        try:
            logging.info("Starting the bot...")
            s.start()
        except Exception as e:
            exception_message = e.message
            if e.message=='not-authorized':
                if checkNewVersion(S40YowsupEnv._VERSION,S40YowsupEnv._TOKEN_STRING):
                    currSettings = json.load(urllib2.urlopen("https://coderus.openrepos.net/whitesoft/whatsapp_scratch"))
                    logging.error("Looks like the WhatsApp token string version was updated. Change the yowsup/env/env_s40.py file with the new values: _VERSION=%s "
                                  "and _TOKEN_STRING=%s{phone} and restart the bot."%(currSettings['e'],currSettings['b']))
                    remaining_shutdown_tries = 0
                    break
                else:
                    logging.error("Re-check your .wcredentials file and assert that you're using the correct login/password.")
            else:
                logging.error("Error: %s"%e)
            logging.error("The bot will be restarted in %s seconds. %s tries remaining until complete shutdown."%(c.time_between_retries,remaining_shutdown_tries))
            time.sleep(c.time_between_retries) # Wait and check again l3ter.
            remaining_shutdown_tries -= 1
    logging.error("Unrecoverable error. Shutting down D2WBot.")
    try:
        if c.boxcar_user_credentials is not None:
            notification_data = {
              'user_credentials':c.boxcar_user_credentials,
              'notification[title]':"D2WBot Down",
              'notification[long_message]':"<b>Your D2WBot instance named ""%s"" is down. Error message: %s. Check the log for more details.</b>"%(c.instance_name,exception_message),
              'notification[source_name]':"D2WBot - OpenShift",
              'notification[sound]':"echo",
            }
            post_data = urllib.urlencode(notification_data)
            urllib2.urlopen("https://new.boxcar.io/api/notifications",post_data)
            logging.error("A BoxCar notification was sent.")
    except Exception as notification_error:
        logging.error("Tried to send notification error, but something bad happened.")