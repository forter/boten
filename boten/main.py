#!/usr/bin/env python
# -*- coding: utf-8 -*-
from ConfigParser import SafeConfigParser, NoSectionError
from importlib import import_module
from boto import sqs
import config
import utils
import logging
import os


def init_bots(parser):

    bots = {}
    bots_enabled = parser.sections()
    bots_enabled.remove('config')
    for bot in bots_enabled:
        logger.info('Initializing bot {}'.format(bot))
        try:
            config = dict(parser.items(bot))
        except NoSectionError:
            config = {}
        repo_name = config.get('repo').split('/')[1]
        if config.get('repo'):
            if not os.path.isdir('repo/' + repo_name):
                logger.info('Cloning {}'.format(config.get('repo')))
                utils.local_cmd('git clone git@github.com:{}.git'.format(config.get('repo')), cwd='repo')
        if not os.path.islink('bots_enabled/{}.py'.format(bot)):
            logger.info('Installing {}'.format(bot))
            utils.local_cmd('ln -s ../repo/{repo_name}/{path} bots_enabled/{bot_name}.py'.format(
                            repo_name=repo_name,
                            path=config.get('location'),
                            bot_name=bot))
        bots.update({bot: import_module('boten.bots_enabled.' + bot).Bot(config)})
    return bots


if __name__ == '__main__':

    parser = SafeConfigParser()
    parser.read('boten.cfg')
    utils.setup_logging(False)
    logger = logging.getLogger("boten")
    sqs_conn = sqs.connect_to_region(config.AWS_REGION)

    queue = sqs_conn.get_queue(config.QUEUE_NAME)
    # queue.clear()
    bots = init_bots(parser)
    logger.info('bots loaded [{}]'.format(",".join(bots.keys())))
    while True:
        logger.info('polling for new job')
        with utils.poll_sqs(queue) as payload:
            logger.info('Got new job')
            bot_name = payload['command'][1:]
            payload['subcommand'] = payload['text'].partition(' ')[0]
            payload['args'] = payload['text'].partition(' ')[2]
            try:
                for message in bots[bot_name].run_command(payload):
                    utils.respond(payload, message)
            except Exception as e:
                logger.exception("Cannot run")
