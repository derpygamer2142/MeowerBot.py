from cleo.commands.command import Command
from cleo.helpers import argument, option

import requests

class CreateBot(Command):
    name = "bot:create"
    description = "Create a new bot"
    arguments = [
        argument(
            "yourusername",
            description="Your username",
            optional=True,
        ),
        argument(
            "yourpassword",
            description="Your password",
            optional=True,
        ),
        argument(
            "botname",
            description="The name of the bot",
            optional=True,
            
        ),
        argument(
            "server",
            description="The server API",
            default="https://api.beta.meower.org/",
            optional=True
        )
    ]

    def handle(self):
        username = self.argument("yourusername")
        password = self.argument("yourpassword")
        botname = self.argument("botname")

        if username is None:
            username = self.ask("What is your username?\n")

        if password is None:
            password = self.ask("What is your password?\n")
        
        if botname is None:
            botname = self.ask("What is the name of the bot?\n")
        
        self.line(f"Logging in as {username}...")
        resp: requests.Response = requests.post(f"{self.argument('server')}v1/auth/password", json={"username": username, "password": password})
        if resp.status_code != 200:
            self.line_error(f"Failed to login: {resp.status_code}")
            self.line_error(resp.text)
            return
        
        token = resp.json()["access_token"]
        self.line("Logged in successfully!")
        self.line(f"Creating application for bot {botname}...")

        resp: requests.Response = requests.post(f"{self.argument('server')}v1/applications", headers={"Authorization": token}, json={"name": botname})

        if resp.status_code != 200:
            self.line_error(f"Failed to create application: {resp.status_code}")
            self.line_error(resp.text)
            return
        
        app_id = resp.json()["id"]
        self.line(f"Created application with ID {app_id}!")

        self.line("Creating bot...")
        resp: requests.Response = requests.post(f"{self.argument('server')}v1/applications/{app_id}/bot", headers={"Authorization": token}, json={"username": botname})

        if resp.status_code != 200:
            self.line_error(f"Failed to create bot: {resp.status_code}")
            self.line_error(resp.text)
            return
        token = resp.json()["token"]
        self.line(f"Created bot with token {token}!")




        
from cleo.application import Application


application = Application()
application.add(CreateBot())

if __name__ == "__main__":
    application.run()