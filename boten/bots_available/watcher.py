from __future__ import absolute_import
from boten import core
import pygerduty
import datetime
from boten.config import watcher as config


class Bot(core.BaseBot):
    def __init__(self):
        super(Bot, self).__init__()
        self.pager = pygerduty.PagerDuty(config.ORG_NAME, config.PAGERDUTY_KEY)

    def command_who(self):
        now = datetime.datetime.now()
        tomorrow = now + datetime.timedelta(days=1)
        bufferstr = ""
        for schedule in self.pager.schedules.list():
            bufferstr += "for *{}* the watcher is:\n".format(schedule.name)
            entries = self.pager.schedules.show(schedule.id)
            entry = next(entries.entries.list(since=now.isoformat(), until=tomorrow.isoformat()))
            info = entry.to_json()
            bufferstr += "> "
            bufferstr += info['user']['name']
            bufferstr += "\n"
        yield bufferstr
