from core import BaseBot
from core import get_enabled_bots


class Bot(BaseBot):

    def command_ping(self, user_name):
        yield "pong {}".format(user_name)

    def command_reload(self):
        raise SystemExit("Reload")

    def command_enabled(self):
        yield ",".join(get_enabled_bots())
