#overloads
from typing import overload, Coroutine, Callable

class Command:
    def __init__(self, function, name=None, max_args=None):
        self.function = function
        self.subcommands = {}
        self.owner = None

        if name is None:
            name = function.__name__
        self.name = name

        self.max_args = max_args


    def register_owner(self, owner):
        self.owner = owner


    async def run_command(self, args):
        if args[0] in self.subcommands:
            await self.subcommands[args[0]].run_command(args[1:])
        else:
            await self.function(args)
    
    def __call__(self, *args, **kwargs):
        raise TypeError("Command is not callable, use Command.run_command instead")
    
    def subcommand(self, coro, name=None, max_args=None):
        if name is None:
            name = coro.__name__
        self.subcommands[name] = Command(coro, name=name, max_args=max_args)
        return coro


class Cog:
    _instence = None
    __commands = {}


    def __init__(self, bot):
        self.__class__._instence = self
        self.bot = bot

        for command in self.__dir__():
            attr = getattr(self, command)
            if isinstance(attr, Command):
                attr.register_class(self)

                self.__commands[command.name] = attr

        self.name = self.__class__.__name__

    
    def __new__(cls, *args, **kwargs):
        if cls._instence is None:
            self = super().__new__(cls)

            return self

        else:
            return cls._instence

    
    @property
    def commands(self):
        return self.__commands

    def delete_command(self, command: str | Command):
        if isinstance(command, Command):
            command = command.name
        del self.__commands[command]


@overload
def command(name=None, max_args=None) -> Callable[[Coroutine], Command]:
    def decorator(coro: Coroutine) -> Command:
        return Command(coro, name=name)
    return decorator

from typing import overload

@overload
def command(coro: Coroutine) -> Command:
    return Command(coro)


