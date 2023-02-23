import sys
import os

# Add the parent directory to the path so we can import the module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncio

from MeowerBot import _http, _websocket


from dotenv import load_dotenv, dotenv_values
from logging import basicConfig, DEBUG

basicConfig(level=DEBUG)
load_dotenv()

env = {
    **dotenv_values(".env"),
    **dotenv_values(".env.local"),
    **os.environ
}

class AioRunner:
    def __init__(self, loop):
        self.loop = loop
        self.token = env["TOKEN"]
        self.wss_url = env["WSS_URL"]   
        self.api_url = env["API_URL"]

        self._http: _http._http = _http._http(self.token)
        self._http.API_URL = self.api_url #type: ignore
        self._websocket: _websocket._websocket = _websocket._websocket()
    
    async def __aenter__(self):

        return self
    
    async def __aexit__(self, exc_type, exc_value, traceback):
        
        await self._http.session.close()
        await self._websocket.client.close()


    async def run(self):
        await self._websocket.run(self.wss_url, self.token)




    

