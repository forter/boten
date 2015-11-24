# global params
# * seilt
# * verbose

from core import BaseBot


class Bot(BaseBot):

    def command_ping(self, user_name, name="moshe"):
        yield "pong {}".format(user_name)

    def command_reload(self):
        raise SystemExit("Reload")
