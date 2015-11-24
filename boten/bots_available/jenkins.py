# global params
# * seilt
# * verbose

from __future__ import absolute_import
from core import BaseBot
import jenkins
import config


class Bot(BaseBot):

    def __init__(self):
        super(Bot, self).__init__()
        self.server = jenkins.Jenkins(config.CI_URL)

    def color(self, job):
        if job['color'] in ['blue', 'blue_anime']:
            return 'good'
        elif job['color'] == 'disabled':
            return '#aba1a1'
        else:
            return 'danger'

    def command_status(self):
        for job in self.server.get_jobs():
            yield {'text': "{} with status {}".format(job['name'], job['color']),
                   'color': self.color(job)}

    def command_failed(self):
        for job in self.server.get_jobs():
            if job['color'] not in ['blue', 'blue_anime', 'disabled']:

                yield {'text': '{} with status {}'.format(job['name'], job['color']),
                       'color': self.color(job)}
