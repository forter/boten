import requests
from bs4 import BeautifulSoup
from core import BaseBot


class Bot(BaseBot):

    def __init__(self):
        super(Bot, self).__init__()
        self.next_time = BeautifulSoup(requests.post('http://devopsreactions.tumblr.com/random').content)

    def command_make_me_laugh(self):
        page = self.next_time
        post_content = page.find("div", {"class": "item_content"})
        yield unicode(page.find('div', {"class": "post_title"}).find('a').contents[0])
        yield post_content.find('img')['src']
        self.next_time = BeautifulSoup(requests.post('http://devopsreactions.tumblr.com/random').content)
