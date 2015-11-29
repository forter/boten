# Boten - python bot for slack

### Write new bot
lets look on example (funBot):
```python
import requests
from bs4 import BeautifulSoup
from boten import core


class Bot(core.BaseBot):

    def command_make_me_laugh(self):
        page = BeautifulSoup(requests.post('http://devopsreactions.tumblr.com/random').content)
        post_content = page.find("div", {"class": "item_content"})
        yield unicode(page.find('div', {"class": "post_title"}).find('a').contents[0])
        yield post_content.find('img')['src']

```
now, if someone will type `/fun make_me_laugh` (or even `/fun mak` cuase boten trying to check for method starting with mak) he will send funny post from [devopsreactions](http://devopsreactions.tumblr.com/)

### Parsing args - Mandatory args
Just create new function and ask for args, Boten will enforce the user for them.
```python
    def command_ping(self, user_name):
        yield "pong {}".format(user_name)
```
`/fun ping` will fail with error message of  
> *Function name:*​ /ping  
> ​*Mandatory args are:*​ user_name  
> ​*Optional args are:*​

### Parsing args - Optional args
```python
    def command_ping(self, user_name="default"):
        yield "pong {}".format(user_name)
```
`/fun ping` will send `pong default`  
but `/fun ping --user_name=moshe` will send `pong moshe`

### Sending messages to slack
you can yield for messages while running, if you want to send message with slide colors you need to use core.SlackMessage
```python
yield core.SlackMessage()
        .icon(':low_brightness:')
        .username('jenkinsBot')
        .text("unitTests failure", color="danger")
```

### help messages
Simply `/fun help`, `/fun ping help`


## Add bot
0. create python file under `bots_available`
0. link from `bots_available` to `bots_enabled`
0. add new slash command in slack ui - [Integrations](https://forter.slack.com/services)
