from __future__ import absolute_import
from boten import core
import pygerduty
import datetime


class Bot(core.BaseBot):
    def __init__(self, config):
        super(Bot, self).__init__(config)
        self.pager = pygerduty.PagerDuty(config['org_name'], config['pagerduty_key'])

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
