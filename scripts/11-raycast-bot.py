from javascript import require, On, Once, AsyncTask, once, off
from simple_chalk import chalk
from utils.vec3_conversion import vec3_to_str
import math

# Requires ./utils/vec3_conversion.py

# Import the javascript libraries
mineflayer = require("mineflayer")
vec3 = require("vec3")

# Global bot parameters
server_host = "localhost"
server_port = 3000
reconnect = True


class MCBot:

    def __init__(self, bot_name):
        self.bot_args = {
            "host": server_host,
            "port": server_port,
            "username": bot_name,
            "hideErrors": False,
        }
        self.reconnect = reconnect
        self.bot_name = bot_name
        self.start_bot()

    # Tags bot username before console messages
    def log(self, message):
        print(f"[{self.bot.username}] {message}")

    # Start mineflayer bot
    def start_bot(self):
        self.bot = mineflayer.createBot(self.bot_args)

        self.start_events()

    # Attach mineflayer events to bot
    def start_events(self):

        # Login event: Triggers on bot login
        @On(self.bot, "login")
        def login(this):

            # Displays which server you are currently connected to
            self.bot_socket = self.bot._client.socket
            self.log(
                chalk.green(
                    f"Logged in to {self.bot_socket.server if self.bot_socket.server else self.bot_socket._host }"
                )
            )

        # Spawn event: Triggers on bot entity spawn
        @On(self.bot, "spawn")
        def spawn(this):
            self.bot.chat("Hi!")

        # Kicked event: Triggers on kick from server
        @On(self.bot, "kicked")
        def kicked(this, reason, loggedIn):
            if loggedIn:
                self.log(chalk.redBright(f"Kicked whilst trying to connect: {reason}"))

        # Chat event: Triggers on chat message
        @On(self.bot, "messagestr")
        def messagestr(this, message, messagePosition, jsonMsg, sender, verified=None):
            if messagePosition == "chat":

                # Quit the bot
                if "quit" in ' '.join(message.split()[1:]):
                    self.bot.chat("Goodbye!")
                    self.reconnect = False
                    this.quit()

                # Look at player
                elif "look at me" in message:

                    # Find all nearby players
                    local_players = self.bot.players

                    # Search for our specific player
                    for el in local_players:
                        player_data = local_players[el]
                        if player_data["uuid"] == sender:
                            vec3_temp = local_players[el].entity.position
                            player_location = vec3(
                                vec3_temp["x"], vec3_temp["y"] + 1, vec3_temp["z"]
                            )

                    # Feedback
                    if player_location:
                        self.log(chalk.magenta(vec3_to_str(player_location)))
                        self.bot.lookAt(player_location, True)
                    else:
                        self.log(f"Player not found.")

                # Look at coords
                elif "look at coords" in message:

                    # Find all nearby players
                    x, y, z = message.split(" ")[-3:]

                    # Feedback
                    block_vec3 = vec3(x, y, z)
                    self.log(chalk.magenta(vec3_to_str(block_vec3)))
                    self.bot.lookAt(block_vec3, True)

                # Look in a particular direction
                elif "look" in message:

                    # Get input
                    direction = message.split()[-1]

                    # Calc yaw/pitch for direction
                    yaw, pitch = 0, 0
                    if direction == "up":
                        pitch = math.pi / 2
                        yaw = self.bot.entity.yaw
                    elif direction == "down":
                        pitch = -math.pi / 2
                        yaw = self.bot.entity.yaw
                    elif direction == "east":
                        yaw = math.pi * 3 / 2
                    elif direction == "south":
                        yaw = math.pi
                    elif direction == "west":
                        yaw = math.pi / 2
                    elif direction == "north":
                        pass
                    elif direction == "left":
                        yaw = self.bot.entity.yaw + math.pi / 2
                    elif direction == "right":
                        yaw = self.bot.entity.yaw - math.pi / 2
                    elif direction == "back":
                        yaw = self.bot.entity.yaw + math.pi
                        pitch = self.bot.entity.pitch

                    # Feedback
                    self.log(
                        chalk.magenta(f"Looking {direction}: {pitch:.2f}/{yaw:.2f}")
                    )
                    self.bot.look(yaw, pitch, True)

                # Say which block the bot is looking at
                elif "what do you see" in message:
                    block = self.bot.blockAtCursor()
                    if block:
                        self.bot.chat(f"Looking at {block.displayName}")
                    else:
                        self.bot.chat("Looking at air")

        # End event: Triggers on disconnect from server
        @On(self.bot, "end")
        def end(this, reason):
            self.log(chalk.red(f"Disconnected: {reason}"))

            # Turn off old events
            off(self.bot, "login", login)
            off(self.bot, "spawn", spawn)
            off(self.bot, "kicked", kicked)
            off(self.bot, "messagestr", messagestr)

            # Reconnect
            if self.reconnect:
                self.log(chalk.cyanBright(f"Attempting to reconnect"))
                self.start_bot()

            # Last event listener
            off(self.bot, "end", end)


# Run function that starts the bot(s)
bot = MCBot("raycast-bot")
