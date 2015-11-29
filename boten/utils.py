import pydoc
import json
from contextlib import contextmanager
import logging
import inspect
from boten import core


def setup_logging(debug):
    logging.basicConfig(level=logging.DEBUG if debug else logging.INFO, datefmt='%H:%M:%S',
                        format='[%(asctime)s] {%(name)33s:%(lineno)3d} %(levelname)8s - %(message)s')


def get_func_doc(fn):
    doc = pydoc.plain(pydoc.render_doc(fn, title='%s')).split('\n')[-2].split(') ')[0] + ')'
    return doc


def respond(payload, response):
    logger = logging.getLogger(inspect.stack()[0][3])
    if type(response) == str or type(response) == unicode:
        core.SlackMessage().channel("#" + payload['channel_name']).text(response)._send()
    elif isinstance(response, core.SlackMessage):
        response.channel("#" + payload['channel_name'])._send()
    else:
        logger.error("Cannot handle message")


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
