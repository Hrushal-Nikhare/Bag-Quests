import os

from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

app = App(token=os.environ["SLACK_BOT_TOKEN"])


@app.event("app_mention")
def event_test(body, say):
    say(f"Hello, <@{body['event']['user']}>! to get started run /bq-start")


@app.command("/bq-start")
def repeat_text(ack, say, command):
    # Acknowledge command request
    ack()
    # first_msg = say(f"<@{command['user_id']}> just started a quest!")
    first_msg = say(f"you just started a quest!")
    thread_ts = first_msg["ts"]
    # say(f"{first_msg}" , thread_ts)
    # say(
    #     f"Hello, <@{command['user_id']}>! Choose an item to stake before starting",
    #     thread_ts=thread_ts,
    # )  # TO Do: Add dropdown menu
    say(
        f"Hello! Choose an item to stake before starting",
        thread_ts=thread_ts,
    )  # TO Do: Add dropdown menu


if __name__ == "__main__":
    SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"]).start()
