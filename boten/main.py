#!/usr/bin/env python
# -*- coding: utf-8 -*-
from importlib import import_module
from boto import sqs
import config
import utils
import core
import logging


def init_bots():

    bots_enabled = core.get_enabled_bots()
    return {bot: import_module('boten.bots_enabled.' + bot).Bot() for bot in bots_enabled}


if __name__ == '__main__':

    utils.setup_logging(False)
    logger = logging.getLogger("boten")
    sqs_conn = sqs.connect_to_region(config.AWS_REGION)

    queue = sqs_conn.get_queue(config.QUEUE_NAME)
    #queue.clear()
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
