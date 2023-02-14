from typing import Generic, ParamSpec, Self, Type, TypeVar

from aiohttp import ClientSession

def logErr(loggerObj):
    def define(fn):
        async def inner(self, *args, **kwargs):
            try:
                return fn(self, *args, **kwargs)
            except BaseException as e:  
                logger = getattr(self, loggerObj)
                logger.exception(e)
                raise e
                
class _http:
    API_URL = "https://api.beta.meower.org/"
    def __init__(self: Self, token: str) -> Self: 
        self.token = token
        self.session = ClientSession(self.API_URL, headers={
            "Authorization": token
        })
       
    
    

        