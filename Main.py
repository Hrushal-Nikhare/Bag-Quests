import os
import json

from slack_bolt.app.async_app import AsyncApp
from slack_bolt.adapter.socket_mode.async_handler import AsyncSocketModeHandler

# Install the Slack app and get xoxb- token in advance
app = AsyncApp(token=os.environ["SLACK_BOT_TOKEN"])

Running_Quests = {}

if logging := False:
    import logging
    logging.basicConfig(level=logging.DEBUG)

class QuestHandler:
    def __init__(self, user_id=None):
        self.say = None
        self.thread_ts = None
        self.ping_user = False  # pings are annyoing
        # if user_id is not None:
        #     self.ping_user = True
        self.user_id = user_id

    async def start_quest(self, init_text, say=None):
        # self.say = say
        if say is not None:
            self.say = say
        # print(init_text)
        if self.ping_user is False:
            init_text = init_text.replace(f"<@{self.user_id}>", "").strip()
        true = True
        root_msg = await self.say(init_text)
        self.thread_ts = root_msg["message"]["ts"]
        # true = True
        await self.say("Item Selection",
            blocks=[
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": "Select an Item to Stake",
                        "emoji": true,
                    },
                },
                {
                    "type": "input",
                    "element": {
                        "type": "static_select",
                        "placeholder": {
                            "type": "plain_text",
                            "text": "Select an item",
                            "emoji": true,
                        },
                        "options": [
                            {
                                "text": {
                                    "type": "plain_text",
                                    "text": ":-potato: Potato",
                                    "emoji": true,
                                },
                                "value": "value-0",
                            },
                            {
                                "text": {
                                    "type": "plain_text",
                                    "text": ":-gp: 10 gp",
                                    "emoji": true,
                                },
                                "value": "value-1",
                            },
                            {
                                "text": {
                                    "type": "plain_text",
                                    "text": ":-kiwi: kiwi",
                                    "emoji": true,
                                },
                                "value": "value-2",
                            },
                        ],
                        "action_id": "static_select-action",
                    },
                    "label": {"type": "plain_text", "text": "Items: ", "emoji": true},
                },
            ],
            thread_ts=self.thread_ts,
        )

    async def say_threaded(self, text , say=None):
        if say is not None:
            self.say = say

        if self.ping_user is False and text is not None:
            text = text.replace(f"<@{self.user_id}>", "").strip()

        await self.say(text, thread_ts=self.thread_ts)
    
    def to_dict(self):
        return {
            'user_id': self.user_id,
            'thread_ts': self.thread_ts,
            'ping_user': self.ping_user,
        }
    @classmethod
    def from_dict(cls, data):
        instance = cls(user_id=data.get('user_id'))
        instance.thread_ts = data.get('thread_ts')
        instance.ping_user = data.get('ping_user')
        return instance

try:
    with open('quests.json', 'r') as f:
        serializable_quests = json.load(f)
except FileNotFoundError:
    serializable_quests = []
    with open('quests.json', 'w') as f:
        json.dump(serializable_quests, f)


quests = [QuestHandler.from_dict(data) for data in serializable_quests]

for quest in quests:
    Running_Quests[quest.user_id] = quest

del quests

@app.command("/bq-start")
async def start_quest(ack, body, say):
    user_id = body["user_id"]
    # print(user_id, type(user_id))
    await ack()
    if user_id in Running_Quests:
        await say(f"<@{user_id}> You already have a quest running")
        return
    else:
        quest_handler = QuestHandler(user_id)
        Running_Quests[user_id] = quest_handler
        await quest_handler.start_quest(f"Hello <@{user_id}>", say)

@app.action("static_select-action")
async def handle_some_action(ack, body, logger,say):
    await ack()
    user_id = body["user"]["id"]
    # print(user_id , type(user_id))
    quest_handler = Running_Quests[user_id]
    print()
    selected_option = body["actions"][0]["selected_option"]
    await quest_handler.say_threaded(f"You have selected {selected_option['text']['text']}",say)
    await quest_handler.say_threaded("Quest Complete!")
    await end_quest(user_id)



async def end_quest(user_id):
    Running_Quests.pop(user_id)
    print(f"Ended quest for {user_id}")

@app.event("app_mention")
async def event_test(event, say):
    await say(f"Hi there, <@{event['user']}>! use /bq-start to start a quest =)")


async def ack_shortcut(ack):
    await ack()


async def main():
    handler = AsyncSocketModeHandler(app, os.environ["SLACK_APP_TOKEN"])
    await handler.start_async()


if __name__ == "__main__":
    import asyncio

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Exiting")
    finally:
        quests = [quest.to_dict() for quest in Running_Quests.values()]
        with open('quests.json', 'w') as f:
            json.dump(quests, f)
        del quests