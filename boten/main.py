#!/usr/bin/env python
# -*- coding: utf-8 -*-
from importlib import import_module
from boto import sqs
import boten
import utils
import logging
import os


def init_bots():

    bots = {}
    config = boten.config.get()
    bots_enabled = config.keys()
    bots_enabled.remove('config')
    for bot in bots_enabled:
        logger.info('Initializing bot {}'.format(bot))
        bot_config = config.get("bot", {})
        repo_name = config.get('repo').split('/')[1]
        if bot_config.get('repo'):
            if not os.path.isdir('boten/repo/' + repo_name):
                logger.info('Cloning {}'.format(bot_config.get('repo')))
                utils.local_cmd('git clone git@github.com:{}.git'.format(bot_config.get('repo')), cwd='boten/repo')
        if not os.path.islink('bots_enabled/{}.py'.format(bot)):
            logger.info('Installing {}'.format(bot))
            utils.local_cmd('ln -s ../repo/{repo_name}/{path} boten/bots_enabled/{bot_name}.py'.format(
                            repo_name=repo_name,
                            path=bot_config.get('location'),
                            bot_name=bot))
        bots.update({bot: import_module('boten.bots_enabled.' + bot).Bot(bot_config)})
    return bots


if __name__ == '__main__':

    utils.setup_logging(False)
    logger = logging.getLogger("boten")
    sqs_conn = sqs.connect_to_region(config.AWS_REGION)

    queue = sqs_conn.get_queue(config.QUEUE_NAME)
    bots = init_bots()
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
