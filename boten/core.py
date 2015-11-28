import shlex
import utils
from glob import glob
import traceback


def respond(payload, response):

        utils.send_slack_message("#" + payload['channel_name'], response, icon=":robot_face:", username='slackBot')


def get_enabled_bots():
    return list({bot.split('/')[2].split('.')[0] for bot in glob('boten/bots_enabled/*py')} - set(['__init__']))


class BaseBot(object):
    def __init__(self):
        self.commands = [method.partition('_')[2] for method in dir(self) if method.startswith('command')]

    def usage(self, func):

        # Parse function args
        func_args = func.__code__.co_varnames
        func_defaults = set(func.func_defaults or [])
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
            .format(name=func.func_name.replace('command_', '/'),
                    man=",".join(func_mandatory_args),
                    optional=",".join(func_optional_args))

    def available_commands(self):
        return [x for x in dir(self) if x.startswith('command_')]

    def run_command(self, payload):
        # Find method staring with gotten command
        prefix_like_commands = [x for x in self.available_commands() if x.startswith('command_' + payload['subcommand'])]
        if len(prefix_like_commands) == 1:
            subcommand = prefix_like_commands[0]
            command_method = getattr(self, subcommand)

            # Parse slack args
            slack_args = shlex.split(payload['args'])
            slack_optional_args = [x for x in slack_args if x.startswith('--')]
            slack_optional_args = {x.split('=')[0][2:]: x.split('=')[1] for x in slack_optional_args}
            slack_mandatory_args = [x for x in slack_args if not x.startswith('--')]

            if len(slack_mandatory_args) != 0 and slack_mandatory_args[0] == "help":
                yield self.usage(command_method)
                return

            try:
                for message in command_method(*slack_mandatory_args, **slack_optional_args):
                    yield message
            except TypeError as e:
                raise
                yield "Got TypeError while processing: {}\n{}".format(e.message, self.usage(command_method))
                yield traceback.format_exc()
        elif len(prefix_like_commands) == 0:
            yield "*Command not found,*\navailable commands are {}".format(self.available_commands())
            return
        else:
            yield "*More then one command starts with {subcommand},*\
                   \nPlease be more specific\
                   \n{avail}".format(subcommand=payload['subcommand'],
                                     avail=", ".join(prefix_like_commands))
            return

    def command_help(self):
        for child in self.available_commands():
            yield self.usage(getattr(self, child))
