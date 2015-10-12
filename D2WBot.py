import sys
import logging

from yowsup.stacks import YowStackBuilder
from yowsup.layers.auth import AuthError

from yowsup.layers import YowLayerEvent

from config import Config
from botLayer import BotLayer


class D2WBot(object):
    # Create the Yowsup stack
    def __init__(self, credentials, encryptionEnabled=True):
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
        except AuthError as e:
            logging.error("Auth Error, reason %s" % e)
        except KeyboardInterrupt:
            # print("\nFucking Scrubs! Signing out!")
            logging.info("D2WBot signing out!")
            sys.exit(0)

if __name__ == "__main__":
    while True:
        try:
            c = Config()  # Load the configurations
            # GTFO Urllib3 logger
            urllib3_logger = logging.getLogger('urllib3')
            urllib3_logger.setLevel(logging.CRITICAL)
            logging.basicConfig(stream=sys.stdout, level=c.log_level, format=c.log_format, datefmt=c.log_date_format)
            s = D2WBot(c.whatsapp_credentials)
            s.__setattr__("config", c)  # Make config accessible to the stack
            while True:
                logging.info("Starting the bot...")
                s.start()
        except Exception, e:
            logging.error("Oh Noes! %s" % e)
