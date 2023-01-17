

class networking:
    def __init__(self, cl):
        self.wss = cl
        self.wss.callback(
            "on_connect", self.__handle_on_connect__
        )  # signing in and stuff like that

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

    def send_msg(self, msg, to="home"):
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

    def send_typing(self, to="home"):
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
       
    def enter_chat(self, chatid="livechat"):
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