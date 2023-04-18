

from MeowerBot import Bot, __version__
from os import environ as env
from logging import basicConfig, DEBUG

basicConfig(level=DEBUG)

bot = Bot()

def login(*_, **__):
	print("login CB")
	bot.send_msg("TESTING!!!!!!!! O_O", to='home')
	bot.send_msg("MeowerBot.py " + __version__, to='home')


def msg(msg, *args, **_):
	print("msg CB")
	if msg.user.username == "Discord": 
		bot.send_msg("TEEEEEST", to="livechat")

bot.callback(login, cbid="login")
bot.callback(msg, cbid="message")

#The env[''] parts can be replaced with strings, which would look like this: 
#bot.run('username', 'password')
#They're environment variables in this example so that no one steals your password and stuff if you post your bot on github.
bot.run(env['username'], env['password'])


