
class BotError(Exception):
    pass

class BotWarning(Warning):
    pass

class InvalidTokenError(BotError):
    pass

class NotAllowedError(BotError):
    pass

