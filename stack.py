import sys

from yowsup.stacks import YowStackBuilder
from yowsup.layers.auth import AuthError

from yowsup.layers import YowLayerEvent

from layer import YowsupCliLayer
from config import Config


class YowsupCliStack(object):
    def __init__(self, credentials, encryptionEnabled=True):
        stackBuilder = YowStackBuilder()

        self.stack = stackBuilder \
            .pushDefaultLayers(encryptionEnabled) \
            .push(YowsupCliLayer) \
            .build()

        # self.stack.setCredentials(credentials)
        self.stack.setCredentials(credentials)

    def start(self):
        print("Yowsup Cli client\n==================\nType /help for available commands\n")
        self.stack.broadcastEvent(YowLayerEvent(YowsupCliLayer.EVENT_START))

        try:
            self.stack.loop(timeout=0.5, discrete=0.5)
        except AuthError as e:
            print("Auth Error, reason %s" % e)
        except KeyboardInterrupt:
            print("\nYowsdown")
            sys.exit(0)


if __name__ == "__main__":
    c = Config()
    s = YowsupCliStack(c.whatsapp_credentials)
    s.start()
    # y = s.stack.getLayer(7)
    # s.L()
    # s.groups_list()
    # sys.exit(0)
    # print c.whatsapp_credentials
