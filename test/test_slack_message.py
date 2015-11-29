#!/usr/bin/env python
# -*- coding: utf-8 -*-

from boten.core import SlackMessage
from boten import config
import requests_mock


def test_text():
    assert SlackMessage().text("test")._text == "test"
    assert SlackMessage().text("test", color="danger")._text == ""


def test_attachments():
    assert len(SlackMessage().text("test", color="danger")._attachments) == 1


def test_channel():
    assert SlackMessage().channel("test")._channel == "test"


def test_icon():
    assert SlackMessage().icon("test")._icon == "test"


def test_username():
    assert SlackMessage().username("test")._username == "test"


def test_clear():
    assert SlackMessage().text("test")._clear()._text == ""


def test_send():
    url = "https://hooks.slack.com/services/%s" % config.SLACK_KEY
    slack = SlackMessage().text("test")
    with requests_mock.mock() as m:
        m.post(url, text='resp')
        slack._send()
        assert m.called
        assert m.call_count == 1
        assert m.request_history[0].json()["text"] == "test"