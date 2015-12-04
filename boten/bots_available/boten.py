from __future__ import absolute_import
from boten import core
from boten import utils
from core import get_enabled_bots


class Bot(core.BaseBot):

    def command_ping(self, user_name):
        yield "pong {}".format(user_name)

    def command_reload(self):
        raise SystemExit("Reload")

    def command_enabled(self):
        yield ",".join(get_enabled_bots())

    def command_pull(self):
        yield utils.local_cmd("git pull")
