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
    first_msg = say(f"<@{command['user_id']}> just started a quest!")
    thread_ts = first_msg["ts"]
    # say(f"{first_msg}" , thread_ts)
    say(
        f"Hello, <@{command['user_id']}>! Choose an item to stake before starting",
        thread_ts=thread_ts,
    )  # TO Do: Add dropdown menu
    say(
        blocks=[
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": f"open the initial screen"},
                "accessory": {
                    "type": "button",
                    "text": {"type": "plain_text", "text": "Click Me"},
                    "action_id": "initial_screen",
                },
            }
        ],
    )


# The open_modal shortcut listens to a shortcut with the callback_id "open_modal"
@app.action("initial_screen")
@app.shortcut("initial_screen")
async def open_modal(ack, body, client):
    # Acknowledge the command request
    await ack()
    # Call views_open with the built-in client
    await client.views_open(
        trigger_id=body["trigger_id"],
        # View payload
        view={
            "type": "modal",
            # View identifier
            "callback_id": "view_1",
            "title": {"type": "plain_text", "text": "initial_screen"},
            "blocks": [
                {
                    "type": "section",
                    "text": {"type": "mrkdwn", "text": f"hi there"},
                    "accessory": {
                        "type": "button",
                        "text": {"type": "plain_text", "text": "Click me"},
                        "action_id": "next_screen"
                    }
                }
            ]
        }
    )


@app.event("app_home_opened")
def update_home_tab(client, event, logger):
    try:
        # Call views.publish with the built-in client
        client.views_publish(
            # Use the user ID associated with the event
            user_id=event["user"],
            # Home tabs must be enabled in your app configuration
            view={
                "type": "home",
                "blocks": [
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": "*Welcome home, <@" + event["user"] + "> :house:*",
                        },
                    },
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": "Learn how home tabs can be more useful and interactive <https://api.slack.com/surfaces/tabs/using|*in the documentation*>.",
                        },
                    },
                ],
            },
        )
    except Exception as e:
        logger.error(f"Error publishing home tab: {e}")


if __name__ == "__main__":
    SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"]).start()
