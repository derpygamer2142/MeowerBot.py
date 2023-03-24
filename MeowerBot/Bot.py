from .types import FeedPost, User, Masquerade, Session
import shlex
# Modeling after nextcord.
import asyncio
import logging
from traceback import format_exception
from .commands import command, Command

from ._http import _http
from ._websocket import _websocket

class Bot:
    __events__ = [
        "on_ready",
        "on_message",
        "on_raw_message",
        "user_update",
        "chat_joined"
    ]
    def __init__(self, prefix=None, owner_id=None, maintainers=None):
        self.prefix = prefix
        self.owner_id = owner_id
        self.maintainers = maintainers

        self.watchers = {}
        self.logger = logging.getLogger("meowerbot")
        self.loaded_cogs = {}
        self._websocket: _websocket = _websocket()
        self._http: _http = None # type: ignore
        self._token = None

    async def _call_events(self, event, *args, **kwargs):
        if event in self.__events__:
            try:
                coro = getattr(self, event)
                coro = coro(*args, **kwargs)
            except AttributeError: # Just in case i forget to add the event too the bot class.
                #make a fake coroutine
                async def coro():
                    pass

                coro = coro()

            watchers = [coro]

            if event in self.watchers:
                for watcher in self.watchers[event]:
                    watchers.append(asyncio.create_task(watcher(*args, **kwargs)))

            exp = await asyncio.gather(*watchers, return_exceptions=True)

            
            #check for errors, and give nthem to the error handler
            for e in exp:
                if isinstance(e, Exception):
                    self.logger.error(format_exception(e))
                    await self._call_events("on_error", e, event, *args, **kwargs)
                
            
            
            




    
    def event(self, coro):
        if coro.__name__ in self.__events__:
            setattr(self, coro.__name__, coro)
        else:
            raise ValueError(f"{coro.__name__} is not a valid event name")
        return coro
    
    
    def add_watcher(self, event, coro):
        if event in self.__events__:
            if event not in self.watchers:
                self.watchers[event] = []
            self.watchers[event].append(coro)
        else:
            raise ValueError(f"{event} is not a valid event name")
        return coro
    

    async def on_ready(self):
        pass # empty default implementation

    async def run_command(self, message):

        #trying to use shlex to split the message, but if it fails, use the old method.
        try:
            args = shlex.split(message.content)
        except ValueError:
            args = message.content.split(" ")


        command = args[0][len(self.prefix):]

        try:
            err = await (asyncio.create_task(self.commands[command](self, message, args))).exception()
        except KeyError:
            err = None

        finally:
            if err:
                self.logger.error(format_exception(err))
                await self._call_events("on_error", err, "command")


    async def on_message(self, message: FeedPost or Comment or Post): 
        if message.author.bot and not message.bridged and message.author.bot.verified:
            return

        if not message.post.startswith(self.prefix):
            return
        
        await self.run_command(message)


    @overload
    def command(self, max_args=None, name=None):
        # Call the command decorator with the bot instance.
        ret = command(max_args=max_args, name=name)

        def inner(coro):
            cmd = ret(coro)
            cmd.register_owner(self)
            self.register_command(cmd)
            return cmd
        return inner
    
    @overload
    def command(self, coro) -> Command:
        cmd = command(coro)
        cmd.register_owner(self)
        self.register_command(cmd)
        return cmd

    def register_command(self, command: Command):
        self.commands[command.name] = command

    def delete_command(self, command: str | Command):
        if isinstance(command, Command):
            command = command.name
        del self.commands[command]



    def register_cog(self, cog):
        for command in cog.commands:
            self.register_command(command)
        
        self.loaded_cogs[cog.__class__.__name__] = cog

    def delete_cog(self, cog):
        for command in cog.commands:
            self.delete_command(command)
            command.owner = None

        del self.loaded_cogs[cog.__class__.__name__]


    async def _on_connect(self):
        data = await self._websocket.send_auth(self.token)

        self.user = Session(
            **data, 
            user=PrivateUser(**data["user"]),
            application=Application(**data["application"]),
            chats=[Chat(**chat) for chat in data["chats"]],
            infractions=[Infraction(**infraction) for infraction in data["infractions"]]
        )

        await self._call_events("on_ready", self.user)
    
    async def __run__(self, token):
        self.token = token
        self._http = _http(token)
        await self._websocket.connect(token)



    


            


    
    
