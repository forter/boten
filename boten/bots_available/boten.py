from __future__ import absolute_import
from boten import core
from boten import utils
from ConfigParser import SafeConfigParser
import glob


class Bot(core.BaseBot):

    def __init__(self, config):
        super(Bot, self).__init__(config)
        self.bots = self.get_enabled_bots()

    @staticmethod
    def get_enabled_bots():
        parser = SafeConfigParser()
        parser.read('boten.cfg')
        bots_enabled = parser.sections()
        bots_enabled.remove('config')
        return bots_enabled

    def command_ping(self, user_name):
        yield "pong {}".format(user_name)

    def command_reload(self):
        raise SystemExit("Reload")

    def command_enabled(self):
        yield ",".join(self.bots)

    def command_pull(self):
        yield utils.local_cmd("git pull")

    def command_pull_all(self):
        for repo in glob.glob('repo/*'):
            yield utils.local_cmd('git pull', cwd=repo)
