import sys

from yowsup.stacks import YowStackBuilder
from yowsup.layers.auth import AuthError
from yowsup.layers import YowLayerEvent

from yowsup_cli.layer import YowsupCliLayer
from config import Config
from botLayer import BotLayer


class BotStack(object):
    def __init__(self, credentials, encryptionEnabled=True):
        stackBuilder = YowStackBuilder()

        self.stack = stackBuilder \
            .pushDefaultLayers(encryptionEnabled) \
            .push(BotLayer) \
            .build()

        self.stack.setCredentials(credentials)

    def start(self):
        print("Starting up!")
        self.stack.broadcastEvent(YowLayerEvent(YowsupCliLayer.EVENT_START))

        try:
            self.stack.loop(timeout=0.5, discrete=0.5)
        except AuthError as e:
            print("Auth Error, reason %s" % e)
        except KeyboardInterrupt:
            print("\nFucking Scrubs! Signing out!")
            sys.exit(0)


if __name__ == "__main__":
    c = Config()  # Read credentials in (~/.wcredentials)
    s = BotStack(c.whatsapp_credentials)
    s.start()