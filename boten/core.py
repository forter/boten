import shlex
import traceback
import logging
import inspect
import json
import requests
from ConfigParser import SafeConfigParser


class Cached(object):
    def __init__(self, func):
        self.func = func
        self.results = {}

    def __call__(self, *args, **kwargs):
        # Format hashable key
        key = self.func.__name__

        # Try to load the cache
        cache = self.results.get(key, "no_cache")

        # If there is no cache
        if cache == "no_cache":
            self.results[key] = self.func(*args, **kwargs)
        return self.results[key]


@Cached
def get_config(init='boten/boten.cfg'):
    parser = SafeConfigParser()
    if len(parser.read(init)) == 0:
        raise IOError('Cannot find config file')
    return parser._sections


def get_bot_conf(section):
    return get_config().get(section, {})


class SlackMessage(object):

    def __init__(self):
        self._text = ""
        self._attachments = []
        self._icon = ':robot_face:'
        self._username = 'Boten'
        self._channel = None

    def _attach(self, attachment):
        self._attachments.append(attachment)
        return self

    def _clear(self):
        self._text = ""
        self._attachments = []
        return self

    def payload_builder(self):
        params = {
            'channel': self._channel,
            'icon_emoji': self._icon,
            'username': self._username}
        if self._text != "":
            params.update({'text': self._text})
        if self._attachments:
            params.update({'attachments': self._attachments})
        return params

    def text(self, text, color=None):
        if color is None:
            self._text = text
        else:
            self._attach({"fallback": text,
                          "color": color,
                          "text": text})
        return self

    def channel(self, channel):
        self._channel = channel
        return self

    def icon(self, icon):
        self._icon = icon
        return self

    def username(self, username):
        self._username = username
        return self

    def _send(self):
        logger = logging.getLogger(inspect.stack()[0][3])
        config = get_config().get("config")
        url = "https://hooks.slack.com/services/%s" % config['slack_key']
        params = self.payload_builder()
        response = requests.post(url, data=json.dumps(params), verify=False)
        self._clear()
        if not response.status_code == 200:
            logger.error("Got error from slack: %s " % response.text)
            logger.error(params)
        return self


class BaseBot(object):
    def __init__(self, config):
        self.commands = [method.partition('_')[2] for method in dir(self) if method.startswith('command')]
        self.config = config
        self.payload = None

    def usage(self, func):

        # Parse function args
        func_args = inspect.getargspec(func).args
        func_defaults = set(inspect.getargspec(func).defaults or [])
        if len(func_defaults) == 0:
            func_optional_args = set()
            func_mandatory_args = set(func_args)
        else:
            func_mandatory_args = set(func_args[:-len(func_defaults)])
            func_optional_args = set(func_args) - func_mandatory_args
        func_mandatory_args -= set(['self'])

        return "> *Function name:* {name}\n\
                > *Mandatory args are:* {man}\n\
                > *Optional args are:* {optional}" \
            .format(name=func.func_name.replace('command_', ''),
                    man=",".join(func_mandatory_args),
                    optional=",".join(func_optional_args))

    def run_command(self, payload):
        self.payload = payload
        # Find method staring with gotten command
        prefix_like_commands = filter(lambda x: x.startswith(payload['subcommand']), self.commands)
        if len(prefix_like_commands) == 1:
            subcommand = prefix_like_commands[0]
            command_method = getattr(self, "command_" + subcommand)

            # Parse slack args
            slack_args = shlex.split(payload['args'].encode('utf8'))
            slack_optional_args = [x for x in slack_args if '=' in x]
            slack_optional_args = {x.partition('=')[0]: x.partition('=')[2] for x in slack_optional_args}
            slack_mandatory_args = [x for x in slack_args if '=' not in x]

            if len(slack_mandatory_args) != 0 and slack_mandatory_args[0] == "help":
                yield self.usage(command_method)
                return

            try:
                for message in command_method(*slack_mandatory_args, **slack_optional_args):
                    yield message
            except TypeError as e:
                yield "Got TypeError while processing: {}\n{}".format(e.message, self.usage(command_method))
                yield traceback.format_exc()
            except Exception as e:
                yield "Got Exception while processing: {}\n{}".format(e.message, self.usage(command_method))
                yield traceback.format_exc()
        elif len(prefix_like_commands) == 0:
            yield "*Command not found,*\navailable commands are:\n{}".format("\n".join(self.commands))
            return
        else:
            yield "*More then one command starts with {subcommand},*\
                   \nPlease be more specific\
                   \n{avail}".format(subcommand=payload['subcommand'],
                                     avail=", ".join(prefix_like_commands))
            return

    def command_help(self):
        for child in self.commands:
            yield self.usage(getattr(self, "command_" + child))
