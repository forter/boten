import shlex
import utils


def respond(payload, response):

    utils.send_pretty_message("#" + payload['channel_name'], response, icon=":robot_face:", username='slackBot')


class BaseBot(object):
    def __init__(self):
        self.commands = [method.partition('_')[2] for method in dir(self) if method.startswith('command')]

    def return_usage(self, func):

        # Parse function args
        func_args = func.__code__.co_varnames
        func_defaults = set(func.func_defaults or [])
        if len(func_defaults) == 0:
            func_optional_args = set()
            func_manetory_args = set(func_args)
        else:
            func_manetory_args = set(func_args[:-len(func_defaults)])
            func_optional_args = set(func_args) - func_manetory_args
        func_manetory_args -= set(['self'])

        return "> *Function name:* {name}\n> *Mandatory args are:* {man}\n> *Optional args are:* {optional}" \
            .format(name=func.func_name.replace('command_', '/'),
                    man=",".join(func_manetory_args),
                    optional=",".join(func_optional_args))

    def run_command(self, payload):
        # Trim / char
        if payload['subcommand'] in self.commands:
            command_method = getattr(self, 'command_{}'.format(payload['subcommand']))

            # Parse slack args
            slack_args = shlex.split(payload['args'])
            slack_optional_args = [x for x in slack_args if x.startswith('--')]
            slack_optional_args = {x.split('=')[0][2:]: x.split('=')[1] for x in slack_optional_args}
            slack_mendatory_args = [x for x in slack_args if not x.startswith('--')]

            if len(slack_mendatory_args) != 0 and slack_mendatory_args[0] == "help":
                yield self.return_usage(command_method)
                return

            try:
                for message in command_method(*slack_mendatory_args, **slack_optional_args):
                    yield message
            except TypeError as e:
                yield "Got TypeError while processing: {}\n{}".format(e.message, self.return_usage(command_method))

    def command_help(self):
        for child in dir(self):
            if child.startswith('command_'):
                yield self.return_usage(getattr(self, child))
