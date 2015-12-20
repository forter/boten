import pydoc
import json
from contextlib import contextmanager
import logging
import inspect
from boten import core
from subprocess import Popen, PIPE


def setup_logging(debug):
    logging.basicConfig(level=logging.DEBUG if debug else logging.INFO, datefmt='%H:%M:%S',
                        format='[%(asctime)s] {%(name)33s:%(lineno)3d} %(levelname)8s - %(message)s')


def get_func_doc(fn):
    doc = pydoc.plain(pydoc.render_doc(fn, title='%s')).split('\n')[-2].split(') ')[0] + ')'
    return doc


def respond(payload, response):
    logger = logging.getLogger(inspect.stack()[0][3])
    if payload['channel_name'] == 'directmessage':
        payload['channel_name'] = '@' + payload['user_name']
    elif not (payload['channel_name'].startswith('@') or payload['channel_name'].startswith('#')):
        payload['channel_name'] = '#' + payload['channel_name']
    if payload['channel_name'].startswith('#'):
        core.SlackMessage().channel(payload['channel_name']).text("{user_name} ran {command} {text}".format(**payload))._send()
    if type(response) == str or type(response) == unicode:
        core.SlackMessage().channel(payload['channel_name']).text(response)._send()
    elif isinstance(response, core.SlackMessage):
        response.channel(payload['channel_name'])._send()
    else:
        logger.error("Cannot handle message")


def local_cmd(cmd, **kwargs):
    logger = logging.getLogger(inspect.stack()[0][3])
    logger.debug("Running: %s" % cmd)
    p = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE, **kwargs)
    exit_code = p.wait()
    if exit_code > 0:
        logger.error("Failed to run %s" % cmd)
        logger.error("stdout: %s" % p.stdout.read())
        logger.error("sterr: %s" % p.stderr.read())
    return p.stdout.read().strip()


@contextmanager
def poll_sqs(queue):
    logger = logging.getLogger(inspect.stack()[0][3])
    # Total wait time when queue is empty is 10 secs
    msg = queue.read(visibility_timeout=3600, wait_time_seconds=10)
    while msg is None:
        print msg
        msg = queue.read(visibility_timeout=3600, wait_time_seconds=10)
    # Parse message
    try:
        msg_obj = json.loads(msg.get_body())
    except ValueError as e:
        logger.warning(msg)
        raise ValueError("{}\nCould not decode msg json: {}".format(e, msg.get_body()))

    yield msg_obj
    queue.delete_message(msg)


def get_username(payload):
    return payload['user_name']
