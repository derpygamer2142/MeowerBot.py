import threading
from typing import NoReturn

import shlex

from . import cloudlink
import sys

import json
import traceback

import requests


import time

from .command import AppCommand
from .context import CTX

import time
import logging

from ._wss import networking

class Bot:
    """
    The Public Interface for MeowerBots

    """
    
    def _t_ping(self):
        while True:
            time.sleep(60)

            self.wss.sendPacket({"cmd": "ping", "val": ""})

    def __init__(self, prefix=None):
        self.wss = cloudlink.CloudLink()
        self.callbacks = {}
        self.networking = networking(self)


        # to be used in start
        self.username = None
        self.password = None
        self.logger_in = False

        self.commands = {}

        self.prefix = prefix
        self._t_ping_thread = threading.Thread(target=self._t_ping, daemon=True)  # (:
        self.logger = logging.getLogger("MeowerBot")
        self.bad_exit = False

        self.cogs = {}
        self.ctxcashe = {}


        # to not do pass though funcs

        self.send_msg = self.networking.send_msg #type: ignore
        self.send_typing = self.networking.send_typing #type: ignore
        self.enter_chat = self.networking.enter_chat #type: ignore
        
    def run_cb(self, cbid, args=(), kwargs=None) -> None:  # cq: ignore
        if cbid not in self.callbacks:
            return  # ignore

        if not kwargs:
            kwargs = {}

        kwargs["bot"] = self
        for callback in self.callbacks[cbid]:
            try:
                callback(
                    *args, **kwargs
                )  # multi callback per id is supported (unlike cloudlink 0.1.7.3 LOL)
            except Exception as e:  # cq ignore

                self.logger.error(traceback.format_exc())
                self.run_cb("error", args=(e))

    def run_command(self, message) -> None:
        args = shlex.split(str(message))

        try:
            self.commands[args[0]]["command"].run_cmd(message.ctx, *args[1:])
        except KeyError as e:
            self.run_cb("error", args=(e,))

    def callback(self, callback, cbid=None) -> None:
        """Connects a callback ID to a callback"""
        if cbid is None:
            cbid = callback.__name__

        if cbid not in self.callbacks:
            self.callbacks[cbid] = []
        self.callbacks[cbid].append(callback)

    def command(self, name=None, args=0) -> None:
        def inner(func):
            if aname is None:
                name = func.__name__
            else:
                name = aname

            cmd = AppCommand(func, name=name, args=args)

            info = cmd.info()
            info[cmd.name]["command"] = cmd

            self.commands.update(info)

            return func

        return inner

    def register_cog(self, cog) -> None:
        info = cog.get_info()
        self.cogs[cog.__class__.__name__] = cog
        self.commands.update(info)

    def deregister_cog(self, cogname) -> None:
        for cmd in self.cogs[cogname].get_info().values():
            del self.commands[cmd.name]
        del self.cogs[cogname]

    def run(self, username, password, server="wss://server.meower.org") -> NoReturn:
        """
        Runs The bot (Blocking)
        """
        self.username = username
        self._password = password
        self.logger_in = True

        self._t_ping_thread.start()
        if self.prefix is None:
            self.prefix = "@" + self.username
        self.logger = logging.getLogger(f"MeowerBot {self.username}")
        self.wss.client(server)

        if self.bad_exit:
            raise BaseException("Bot Account Softlocked")
