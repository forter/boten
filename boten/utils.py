import pydoc
import json
from contextlib import contextmanager
import logging
import inspect
import requests
import config


def setup_logging(debug):
    logging.basicConfig(level=logging.DEBUG if debug else logging.INFO, datefmt='%H:%M:%S',
                        format='[%(asctime)s] {%(name)33s:%(lineno)3d} %(levelname)8s - %(message)s')


def get_func_doc(fn):
    doc = pydoc.plain(pydoc.render_doc(fn, title='%s')).split('\n')[-2].split(') ')[0] + ')'
    return doc


def send_slack_message(channel, message, icon=":tada:", username='deployBot'):
    logger = logging.getLogger(inspect.stack()[0][3])
    url = "https://hooks.slack.com/services/%s" % config.SLACK_KEY
    params = {
        'channel': channel,
        'icon_emoji': icon,
        'username': username}
    if type(message) == str or type(message) == unicode:
        params.update({'text': message})
    elif type(message) == list:
        params.update({'attachments': [{"fallback": m['text'],
                       "color": m['color'],
                       "text": m['text']} for m in message]})
    elif type(message) == dict:
        params.update({'attachments': [{"fallback": message['text'],
                                        "color": message['color'],
                                        "text": message['text']}]})
    else:
        logger.error('Unknown format')
    response = requests.post(url, data=json.dumps(params), verify=False)
    if not response.status_code == 200:
        logger.error("Got error from slack: %s " % response.text)


@contextmanager
def poll_queue(queue):
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
