from javascript import require, On, Once, AsyncTask, once, off

# Import the javascript libraries
mineflayer = require("mineflayer")

# Create bot
bot_args = {"username": "reconnect-bot", "host": "localhost", "port": 3000, "version": "1.19.4", "hideErrors": False}

reconnect = True

def start_bot():
    bot = mineflayer.createBot(bot_args)

    # Login event (Logged in)
    @On(bot, "login")
    def login(this):
        bot_socket = bot._client.socket
        print(
            f"Logged in to {bot_socket.server if bot_socket.server else bot_socket._host }"
        )

    # Kicked event (Got kicked from server)
    @On(bot, "kicked")
    def kicked(this, reason, loggedIn):
        if loggedIn:
            print(f"Kicked whilst trying to connect: {reason}")

    # Chat event (Received message in chat)
    @On(bot, "messagestr")
    def messagestr(this, message, messagePosition, jsonMsg, sender, verified):
        if messagePosition == "chat" and "quit" in message:
            global reconnect
            reconnect = False
            this.quit()

    # End event (Disconnected from server)
    @On(bot, "end")
    def end(this, reason):
        print(f"Disconnected: {reason}")
        off(bot, "login", login)
        off(bot, "kicked", kicked)
        off(bot, "messagestr", messagestr)
        if reconnect:
            print("RESTARTING BOT")
            start_bot()
        off(bot, "end", end)


# Run function that starts the bot
start_bot()
