from collections import namedtuple
from dataclasses import dataclass
from typing import Any, NamedTuple, Optional
import asyncio
import json
import logging
import uuid

from websockets.legacy.client import connect, WebSocketClientProtocol

from .errors import InvalidTokenError
from .types import WaitReturn, Statuscode

import traceback
class _websocket:
    def __init__(self):
        self.client: WebSocketClientProtocol = None  # type: ignore
        self._awaiting_packet = {}
        self.cbs = {}
        self.rooms = rooms()
        self.token = None

        self.logger = logging.getLogger("MeowerBot.websocket")

    async def run_callback(self, id, *args, **kwargs):

        if id not in self.cbs:
            self.logger.debug(f"No callback found for ID {id}")
            return

        self.logger.debug(f"Running callback for ID {id}")

        coros = [cb(*args, **kwargs) for cb in self.cbs[id]]
        ret = await asyncio.gather(*coros)

        # Check for any errors
        for r in ret:
            if isinstance(r, Exception):
                self.logger.error(traceback.format_exc())
                self.run_callback("error", r)

    async def waiting_for(self, packet: dict):
        listener = packet.get("listener")
        if packet["cmd"] == "statuscode":
            self._awaiting_packet[listener]["ok"] = packet["code_id"] == 100
            self._awaiting_packet[listener]["statuscode"].update(packet)

            if "value" in packet and self._awaiting_packet[listener]["packet"] == None:
                self._awaiting_packet[listener]["packet"] = packet["value"]

            self._awaiting_packet[listener]["event"].set()

        elif self._awaiting_packet[listener]["packet"] == None:
            del packet["listener"]
            self._awaiting_packet[listener]["packet"] = packet
        elif type(self._awaiting_packet[listener]["packet"]) != list:
            self._awaiting_packet[listener]["packet"] = [
                self._awaiting_packet[listener]["packet"],
                packet,
            ]
        else:
            self._awaiting_packet[listener]["packet"].append(packet)

    # https://github.com/MikeDev101/cloudlink/blob/97b5edeac82f87ce6b04a2b5581b3e83e40c419f/cloudlink/async_client/async_client.py#L505-L531
    async def userlist(self, message):
        room_data: Optional[rooms.__room__] = None
        if "rooms" in message:
            # Automatically create room and update the global data value
            self.rooms.create(message["rooms"])
            room_data = self.rooms.get(message["rooms"])
        else:
            # Assume a gmsg with no "rooms" value is the default room
            room_data = self.rooms.get("default")

        # Interpret and execute ulist method
        if room_data is None:
            return

        if "mode" in message:
            if message["mode"] in ["set", "add", "remove"]:
                match message["mode"]:
                    case "set":
                        room_data.userlist = message["val"]
                    case "add":
                        if not message["val"] in room_data.userlist:
                            room_data.userlist.append(message["val"])
                    case "remove":
                        if message["val"] in room_data.userlist:
                            room_data.userlist.remove(message["val"])
            else:
                self.logger.error(
                    f"Could not understand ulist method: {message['mode']}"
                )
        else:
            # Assume old userlist method
            room_data.userlist = set(message["val"])

        self.logger.info(f"::[{room_data.name}] Ulist {room_data.userlist}")
        await self.run_callback("ulist", room_data.userlist, room_data)

    async def statuscode(self, packet):
        listener: str | None = packet.get("listener")
        print("Got statuscode", packet)

        if listener == "protocolset":
            resp: WaitReturn = await self.send_auth(self.token)

            if not resp.ok:
                raise InvalidTokenError(
                    f"The Token provided is invalid, {resp.statuscode.code}"
                )
            
            self.logger.info("Authenticated")
            await self.run_callback("auth", resp.packet)

    async def __packet__(self, packet: dict):
        self.logger.debug(f"Got Packet: {packet}")

        listener = packet.get("listener")
        if packet["cmd"] == "statuscode":
            try:
                await self.statuscode(packet)
            except Exception as e:
                self.logger.error(traceback.format_exc())
            


        if packet["cmd"] == "ulist":
            try:
                await (self.userlist(packet))
            except Exception as e:
                self.logger.error(traceback.format_exc())

        if (
            listener in self._awaiting_packet
        ):  # THIS IS VERY DEPENDENT ON ORDER OF SENDING
            self.logger.debug(f"Packet is waiting for {listener}: {packet['cmd']}")
            try:
                await self.waiting_for(packet)
            except Exception as e:
                self.logger.error(traceback.format_exc())



    async def send_packet(self, packet):
        self.logger.debug(f"Sending Packet: {packet}")
        await self.client.send(json.dumps(packet))

    async def send_and_recv(self, packet: dict):
    
        await self.send_packet(packet)

        packet = await self.client.recv()

        data = json.loads(packet)

        return data

    async def send_listener(self, packet: dict):
        if not packet.get("listener"):
            packet["listener"] = uuid.uuid4().hex

        raw_status  = await self.send_and_recv(packet)

        if raw_status["cmd"] != "statuscode":
            raise Exception("Expected statuscode, got", raw_status)

        status = Statuscode(raw_status["code_id"], raw_status["code"])
        return WaitReturn(status.code_id == 100, packet, status)




    async def send_auth(self, token):
        return await self.send_listener({"cmd": "authenticate", "val": token, "listener": "auth"})


    async def run(self, ip, token):
        self.token = token
        async for client in connect(ip):
            self.client = client

            await self.send_packet(
                {"cmd": "handshake", "listener": "protocolset"}
            )

            self.logger.info(f"Connected to {ip}")

            while self.client.open:
                try:
                    data = json.loads(await self.client.recv())
                    await self.__packet__(data)
                except Exception as e:
                    await self.run_callback("error", e)
                    self.logger.exception(e)


# https://github.com/MikeDev101/cloudlink/blob/97b5edeac82f87ce6b04a2b5581b3e83e40c419f/cloudlink/async_client/async_client.py#L160-L632


class rooms:
    def __init__(self):
        self.default = self.__room__()
        self.default.name = "default"

    def get_all(self):
        return self.__dict__

    def exists(self, room_id: str):
        return hasattr(self, str(room_id))

    def create(self, room_id: str):
        if not self.exists(str(room_id)):
            room = self.__room__()
            room.name = room_id
            setattr(self, str(room_id), room)

    def delete(self, room_id: str):
        if self.exists(str(room_id)):
            delattr(self, str(room_id))

    def get(self, room_id: str):
        if self.exists(str(room_id)):
            return getattr(self, str(room_id))
        else:
            return None

    class __room__:
        def __init__(self):
            # Global data stream current value
            self.global_data_value = str()
            self.name = ""

            # Private data stream current value
            self.private_data_value = {"origin": str(), "val": None}

            # Storage of all global variables / Scratch Cloud Variables
            self.global_vars = dict()

            # Storage of all private variables
            self.private_vars = dict()

            # User management
            self.userlist = list()
