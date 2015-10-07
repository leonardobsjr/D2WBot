import os.path


# Whatsapp Credentials
class Config(object):
    def __init__(self):
        whatsapp_credentials_file = os.path.expanduser("~/.wcredentials")
        with open(whatsapp_credentials_file) as f:
            self.whatsapp_credentials = [line.rstrip('\n') for line in f.readlines()]
