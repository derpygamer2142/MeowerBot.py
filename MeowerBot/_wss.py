

class networking:
    def __init__(self, bot):
        self.bot = bot
        self.bot.wss.callback(
            "on_connect", self.__handle_on_connect__
        )  # signing in and stuff like that

        self.bot.wss.callback(
            "on_packet", self._debug_fix
        )  # self._debug_fix catches all errors

        self.bot.wss.callback("on_error", self.__handle_error__)  # handle uncought errors
        self.bot.wss.callback("on_close", self.__handle_close__)  # Websocket disconnected

    def login(self, username, password):
            self.wss.sendPacket(
                {
                    "cmd": "direct",
                    "val": {
                        "cmd": "authpswd",
                        "val": {"username": username, "pswd": password},
                    },
                    "listener": "__meowerbot__login",
                }
            )

    def __handle_on_connect__(self):
        self.wss.sendPacket(
            {
                "cmd": "direct",
                "val": {
                    "cmd": "ip",
                    "val": requests.get("https://api.meower.org/ip").text,
                },
                "listener": "__meowerbot__send_ip",
            }
        )

        self.wss.sendPacket(
            {
                "cmd": "direct",
                "val": {"cmd": "type", "val": "py"},
            }
        )
        self.wss.sendPacket(
            {
                "cmd": "direct",
                "val": "meower",
                "listener": "__meowerbot__cloudlink_trust",
            }
        )

    def send_msg(self, msg, to="home") -> None:
        if to == "home":
            self.wss.sendPacket(
                {
                    "cmd": "direct",
                    "val": {"cmd": "post_home", "val": msg},
                    "listener": "__meowerbot__send_message",
                }
            )
        else:
            self.wss.sendPacket(
                {
                    "cmd": "direct",
                    "val": {"cmd": "post_chat", "val": {"chatid": to, "p": msg}},
                    "listener": "__meowerbot__send_message",
                }
            )

    def send_typing(self, to="home") -> None:
        if  to == "home":
            self.wss.sendPacket(
                {
                    "cmd": "direct",
                    "val": {
                        "cmd": "set_chat_state",
                        "val": {
                            "chatid": "livechat",
                            "state": 101,
                        },
                    },
                }
            )
        else:
          self.wss.sendPacket(
            {
                "cmd": "direct",
                "val": {
                    "cmd": "set_chat_state",
                    "val": {
                        "chatid": to,
                        "state": 100,
                    },
                },
            }
          )
       
    def enter_chat(self, chatid="livechat") -> None:
        self.wss.sendPacket(
            {
                "cmd": "direct",
                "val": {
                    "cmd": "set_chat_state",
                    "val": {
                        "chatid": chatid,
                        "state": 1,
                    },
                },
            }
        )

    def __handle_error__(self, e):
        self.bot.run_cb("error", args=(e))

    def _debug_fix(self, packet):
        if type(packet) is str:
          packet = json.loads(packet)  # Server bug workaround
        

        try:
            self.bot.__handle_packet__(packet)
        except Exception as e:  # cq: skip #IDC ABOUT GENERAL EXCP

            self.bot.logger.error(traceback.format_exc())
            self.bot.run_cb("error", args=(e))

        try:
            self.bot.run_cb("__raw__", args=(packet))  # raw packets
        except Exception as e:  # cq: skip #IDC ABOUT GENERAL EXCP
            self.bot.logger.error(traceback.format_exc())
            self.bot.run_cb("error", args=(e))

    def _handle_status(self, status, listener):
        if status == "I:112 | Trusted Access enabled":
            return
        if self.bot.logger_in:
            self.bot.logger_in = False
            if not status == "I:100 | OK":
                raise RuntimeError("CloudLink Trust Failed")

            self.bot.networking.login(self.bot.username, self.bot._password)

        elif listener == "__meowerbot__login":
            if status == "E:104 | Internal":
                requests.post(
                    "https://webhooks.meower.org/post/home",
                    json={
                        "post": "ERROR: MeowerBot.py Webhooks Logging\n\n Account Softlocked.",
                        "username": self.bot.username,
                    },
                )
                print("CRITICAL ERROR! ACCOUNT SOFTLOCKED!!!!.", file=sys.__stdout__)
                self.bot.bad_exit = True
                self.bot.wss.stop()
                return

            if not status == "I:100 | OK":
                raise RuntimeError("Password Or Username Is Incorrect")

            time.sleep(0.5)
            self.bot.run_cb("login", args=(), kwargs={})

        elif listener == "__meowerbot__send_message":
            if status == "I:100 | OK":
                return  # This is just checking if a post went OK

            raise RuntimeError("Post Failed to send")

    def __handle_close__(self, *args, **kwargs):
        self.bot.run_cb("close", args=args, kwargs=kwargs)

    def discord_support(self, packet):
            if packet["val"]["u"] == "Discord" and ": " in packet["val"]["p"]:
                split = packet["val"]["p"].split(": ")
                packet["val"]["p"] = split[1]
                packet["val"]["u"] = split[0]


            if packet['val']['u'] == "Webhooks" and ": " in  packet["val"]["p"]:
               packet["val"]["p"] = split[1]

            return packet

    def __handle_packet__(self, packet):
        if packet["cmd"] == "statuscode":

            self.bot._handle_status(packet["val"], packet.get("listener", None))

            listener = packet.get("listener", None)
            return self.bot.run_cb("statuscode", args=(packet["val"], listener))

        elif packet["cmd"] == "ulist":
            self.bot.run_cb("ulist", self.bot.wss.statedata["ulist"]["usernames"])

        elif packet["cmd"] == "direct" and "post_origin" in packet["val"]:


            
            
            if "message" in self.bot.callbacks:
                packet = self.discord_support(packet)
                ctx = CTX(packet["val"], self)

                try:
                   self.bot.run_cb("message", args=(ctx.message,))
                except Exception as e:  # cq ignore

                  self.bot.logger.error(traceback.format_exc())
                  self.bot.run_cb("error", args=(e))

            elif self.bot.commands: # Empty dicts eval as false
                packet = self.discord_support(packet)

                ctx = CTX(packet["val"], self)
                if ctx.user.username == self.bot.username:
                    return
                if not ctx.message.data.startswith(self.bot.prefix):
                    return

                ctx.message.data = ctx.message.data.split(self.bot.prefix, 1)[1]

                try:
                  self.bot.run_command(ctx.message)
                except Exception as e:  # cq ignore

                  self.bot.logger.error(traceback.format_exc())
                  self.bot.run_cb("error", args=(e))

                  
            try:
              self.bot.run_cb("raw_message", args=(packet["val"]))
            except Exception as e:  # cq ignore

                self.bot.logger.error(traceback.format_exc())
                self.bot.run_cb("error", args=(e))

        elif packet["cmd"] == "direct":
            listener = packet.get("listener")
            self.bot.run_cb("direct", args=(packet["val"], listener))

        else:
            listener = packet.get("listener")
            self.bot.run_cb(packet["cmd"], args=(packet["val"], listener))
