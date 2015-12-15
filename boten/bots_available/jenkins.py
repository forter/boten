from __future__ import absolute_import
from boten import core
import jenkins
from collections import defaultdict


class Bot(core.BaseBot):

    def __init__(self, config):
        super(Bot, self).__init__(config)
        self.server = jenkins.Jenkins(config['url'])
        self.slack = core.SlackMessage().icon(':low_brightness:').username('jenkinsBot')

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
        for job in self.get_jobs().items():
            self.slack.text("\n".join(job[1]), color=job[0])
        yield self.slack

    def command_failed(self):
        jobs = self.get_jobs()
        yield self.slack.text("\n".join(jobs["danger"]), color="danger")
