import sys
import logging
import time

from yowsup.stacks import YowStackBuilder
from yowsup.layers.auth import AuthError
from yowsup.layers import YowLayerEvent

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
            logging.error("Auth Error, reason %s" % au)
            self.stack.broadcastEvent(YowLayerEvent(BotLayer.EVENT_SHUTDOWN))
        except KeyboardInterrupt:
            logging.info("D2WBot signing out!")
            sys.exit(0)
        except Exception as ex:
            logging.error("Exception: %s" % ex)
            self.stack.broadcastEvent(YowLayerEvent(BotLayer.EVENT_SHUTDOWN))

if __name__ == "__main__":
    c = Config()  # Load the configurations
    # GTFO Urllib3 logger
    urllib3_logger = logging.getLogger('urllib3')
    urllib3_logger.setLevel(logging.CRITICAL)
    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.basicConfig(stream=sys.stdout, level=c.log_level, format=c.log_format, datefmt=c.log_date_format)
    remaining_shutdown_tries = 10 # 10 Tries till error
    while remaining_shutdown_tries > 0:
        try:
            s = D2WBot(c.whatsapp_credentials, False)
            s.__setattr__("config", c)  # Make config accessible to the stack
            logging.info("Starting the bot...")
            s.start()
            logging.info("Something happened! Restarting the bot in one minute.")
            time.sleep(60) # Wait and check again l3ter.
            remaining_shutdown_tries -= 1
        except Exception, e:
            logging.error("Oh Noes! %s" % e)