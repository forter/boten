#!/usr/bin/env python
# -*- coding: utf-8 -*-
from importlib import import_module
from boto import sqs
import boten
import utils
import logging
import os
import click
import multiprocessing


def init_bots():
    logger = logging.getLogger("init_bots")
    bots = {}
    config = boten.core.get_config()
    bots_enabled = config.keys()
    bots_enabled.remove('config')
    # import pdb; pdb.set_trace()
    for bot in bots_enabled:
        logger.info('Initializing bot {}'.format(bot))
        bot_config = config.get(bot, {})
        repo_name = bot_config.get('repo').split('/')[1]
        if bot_config.get('repo'):
            if not os.path.exists('boten/repo/' + repo_name):
                logger.info('Cloning {}'.format(bot_config.get('repo')))
                utils.local_cmd('git clone git@github.com:{}.git'.format(bot_config.get('repo')), cwd='boten/repo')
        if not os.path.islink('boten/bots_enabled/{}.py'.format(bot)):
            logger.info('Installing {}'.format(bot))
            utils.local_cmd('ln -s ../repo/{repo_name}/{path} boten/bots_enabled/{bot_name}.py'.format(
                            repo_name=repo_name,
                            path=bot_config.get('location'),
                            bot_name=bot))
        bots.update({bot: import_module('boten.bots_enabled.' + bot).Bot(bot_config)})
    return bots


def run_payload(bot, payload, logger):
    try:
        for message in bot.run_command(payload):
            utils.respond(payload, message)
    except Exception:
        logger.exception("Cannot run")


@click.command()
@click.option('-c', '--conf-file', default='boten/boten.cfg', help='Boten config file')
def main(conf_file):
    utils.setup_logging(False)
    logger = logging.getLogger("boten")
    config = boten.core.get_config(init=conf_file)
    sqs_conn = sqs.connect_to_region(config['config']['aws_region'])

    queue = sqs_conn.get_queue(config['config']['queue_name'])
    bots = init_bots()
    logger.info('bots loaded [{}]'.format(",".join(bots.keys())))
    while True:
        logger.info('polling for new job')
        with utils.poll_sqs(queue) as payload:
            logger.info('Got new job')
            bot_name = payload['command'][1:]
            if payload['token'] != config[bot_name]['slack_token']:
                logger.warning('Got unauthorized slack command')
                logger.warning(payload)
                continue
            payload['subcommand'] = payload['text'].partition(' ')[0]
            payload['args'] = payload['text'].partition(' ')[2]
            p = multiprocessing.Process(target=run_payload, args=(bots[bot_name], payload, logger))
            p.start()

if __name__ == '__main__':
    main()
