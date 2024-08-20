# import logging

# logging.basicConfig(level=logging.DEBUG)

import os

from slack_bolt.app.async_app import AsyncApp
from slack_bolt.adapter.socket_mode.async_handler import AsyncSocketModeHandler

# Install the Slack app and get xoxb- token in advance
app = AsyncApp(token=os.environ["SLACK_BOT_TOKEN"])


class QuestHandler:
    def __init__(self):
        self.say = None
        self.thread_ts = None
        self.ping_user = False

    async def start_quest(self, init_text, say=None):
        # self.say = say
        if say is not None:
            self.say = say
        print(init_text)
        if self.ping_user is False:
            init_text = init_text.replace("<@", " ")
            init_text = init_text.replace(">", " ")
        print(init_text)
        root_msg = await self.say(init_text)
        self.thread_ts = root_msg["message"]["ts"]
        await self.say_threaded("Choose a item to stake")

    async def say_threaded(self, text):
        if self.ping_user is False:
            text = text.replace("<@", "")
            text = text.replace(">", "")
        
        await self.say(text, thread_ts=self.thread_ts)


# old
# @app.command("/bq-start")
# async def hello_command(ack, body , say):
#     user_id = body["user_id"]
#     # await ack()
#     # root_msg = await say(f"<@{user_id}> Has just Started a Quest!")
#     root_msg = await say("You Have just Started a Quest!")
#     thread_ts=root_msg['message']['ts']
#     # await say(f'{root_msg['message']['ts']}')
#     await say_threaded("Choose a message to stake",say)


@app.command("/bq-start")
async def start_quest(ack, body, say):
    user_id = body["user_id"]
    # await ack()
    quest_handler = QuestHandler()
    await quest_handler.start_quest(f"Hello <@{user_id}>!", say)


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

    asyncio.run(main())
