from boten.core import BaseBot
import payloads


class TestBot(BaseBot):

    def command_arg_bot(self, user_name):
        yield "hello {}".format(user_name)

    def command_no_arg_bot(self):
        yield "hello"

    def command_optional_arg_bot(self, optional="default"):
        yield "hello {}".format(optional)

    def command_two_message_bot(self):
        yield "message1"
        yield "message2"

    def foo(self):
        pass


def test_available_commands():
    bot = TestBot({})
    available_commands = bot.commands
    assert "arg_bot" in available_commands
    assert "no_arg_bot" in available_commands
    assert "optional_arg_bot" in available_commands
    assert "two_message_bot" in available_commands
    assert "foo" not in available_commands


def test_arg_bot_with_arg():
    bot = TestBot({})
    response = list(bot.run_command(payloads.arg_bot_with_arg))
    assert response[0] == "hello derp"


def test_arg_bot_with_no_args():
    bot = TestBot({})
    response = list(bot.run_command(payloads.arg_bot_with_no_args))
    assert response[0].startswith("Got TypeError")  # Help message


def test_no_arg_bot_without_arg():
    bot = TestBot({})
    response = list(bot.run_command(payloads.no_arg_bot_without_arg))
    assert response[0] == "hello"


def test_no_arg_bot_with_arg():
    bot = TestBot({})
    response = list(bot.run_command(payloads.no_arg_bot_with_arg))
    assert response[0].startswith("Got TypeError")  # Help message


def test_optional_arg_bot_with_optional_arg():
    bot = TestBot({})
    response = list(bot.run_command(payloads.optional_arg_bot_with_optional_arg))
    assert response[0] == 'hello derp'


def test_optional_arg_bot_with_no_arg():
    bot = TestBot({})
    response = list(bot.run_command(payloads.optional_arg_bot_with_no_arg))
    assert response[0] == 'hello default'


def test_two_message_bot():
    bot = TestBot({})
    response = list(bot.run_command(payloads.two_message_bot))
    assert len(response) == 2


def test_help_subcommand():
    bot = TestBot({})
    response = list(bot.run_command(payloads.no_arg_bot_with_arg))
    assert response[0].startswith("Got TypeError")  # Help message
