import os
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

# Initializes your app with your bot token and socket mode handler
app = App(token=os.environ.get("SLACK_BOT_TOKEN"))

# The echo command simply echoes on command
@app.command("/test")
def repeat_text(ack, respond, command):
    # Acknowledge command request
    ack()
    respond(f"{command['text']}")

@app.command("/start")
def start(ack, respond, command):
    ack()
    respond("Starting the quest!")

@app.command("/ping")
def ping(ack, respond, command):
    ack()
    respond("Pong")


# Start your app
if __name__ == "__main__":
    SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"]).start()