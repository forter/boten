from __future__ import absolute_import
from boten.core import BaseBot
import jenkins
import config
from collections import defaultdict


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

    def get_jobs(self):
        jobs = defaultdict(list)
        for job in self.server.get_jobs():
            jobs[self.color(job)].append(job['name'])
        return jobs

    def command_status(self):
        jobs = self.get_jobs()
        yield [{"text": "\n".join(x[1]), "color": x[0]} for x in jobs.items()]

    def command_failed(self):
        jobs = self.get_jobs()
        yield {"text": "\n".join(jobs["danger"]), "color": "danger"}
