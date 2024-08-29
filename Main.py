import os
import json
from multiprocessing import Process ,  Manager
import json

from bag import bag_instance

import asyncio
from google.protobuf.json_format import MessageToDict
from slack_bolt.app.async_app import AsyncApp
from slack_bolt.adapter.socket_mode.async_handler import AsyncSocketModeHandler

app = AsyncApp(token=os.environ["SLACK_BOT_TOKEN"])

bag_instance.configure(
    int(os.environ["BAG_ID"]), os.environ["BAG_TOKEN"], os.environ["BAG_OWNER"]
)


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
        self.stake_item = None
        self.approved = False

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
        await self.say(
            "Item Selection",
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
                                    "text": ":-carrot: Carrot",
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

    async def say_threaded(self, text, say=None):
        if say is not None:
            self.say = say

        if self.ping_user is False and text is not None:
            text = text.replace(f"<@{self.user_id}>", "").strip()

        await self.say(text, thread_ts=self.thread_ts)

    def to_dict(self):
        return {
            "user_id": self.user_id,
            "thread_ts": self.thread_ts,
            "ping_user": self.ping_user,
        }

    @classmethod
    def from_dict(cls, data):
        instance = cls(user_id=data.get("user_id"))
        instance.thread_ts = data.get("thread_ts")
        instance.ping_user = data.get("ping_user")
        return instance


try:
    with open("quests.json", "r") as f:
        serializable_quests = json.load(f)
except FileNotFoundError:
    serializable_quests = []
    with open("quests.json", "w") as f:
        json.dump(serializable_quests, f)

def load_quests():
    global Running_Quests
    quests = [QuestHandler.from_dict(data) for data in serializable_quests]

    for quest in quests:
        Running_Quests[quest.user_id] = quest

    del quests

load_quests()

@app.command("/bq-start")
async def start_quest(ack, body, say):
    global Running_Quests
    user_id = body["user_id"]
    await ack()
    if user_id in Running_Quests:
        await say(f"<@{user_id}> You already have a quest running")
        return
    else:
        quest_handler = QuestHandler(user_id)
        Running_Quests[user_id] = quest_handler
        await quest_handler.start_quest(f"Hello <@{user_id}>", say)
        # await quest_handler.say_threaded(f"{bag_instance.get_inventory(user_id)}")
    return


@app.command("/bq-wipe")
async def clear_pending(ack, body, respond):
    user_id = body["user_id"]
    if user_id != 'U03V4B5H8DP':
        await ack()
        await respond(
            f"Hey <@{user_id}>, only the owner can interact with the options."
        )
        return
    else:
        n = len(Running_Quests)
        Running_Quests.clear()
        await ack()
        await respond(f"Wiped {n} quests")
    recive_item = [{"itemName": "Carrot", "quantity": 1}]
    offer_item = []
    return_val = bag_instance.make_offer(
        target_identity_id=user_id,
        offer_to_give=recive_item,
        offer_to_receive=offer_item,
    )


@app.action("static_select-action")
async def handle_some_action(ack, body, logger, say, respond):
    global Running_Quests
    user_id = body["user"]["id"]
    try:
        quest_handler = Running_Quests[user_id]
    except KeyError:
        await ack()
        await respond(
            f"Hey <@{user_id}>, You have already chosen an item or all quests have been wiped."
        )
        return

    if user_id != quest_handler.user_id:
        await ack()
        await respond(
            f"Hey <@{user_id}>, only the quest owner can interact with the options."
        )
        return

    # print(user_id)
    await ack()
    selected_option = body["actions"][0]["selected_option"]
    await quest_handler.say_threaded(
        f"You have selected {selected_option['text']['text']}", say
    )
    quest_handler.stake_item = selected_option["text"]["text"].split(" ")[-1]

    inventory = MessageToDict(bag_instance.get_inventory(user_id))

    item_present = False

    for item in inventory["inventory"]:
        if item["itemId"] == quest_handler.stake_item:
            item_present = True
            break

    if not item_present:
        await quest_handler.say_threaded(
            f"You do not have the item {quest_handler.stake_item}"
        )
        await quest_handler.say_threaded("Quest Failed!")
        await end_quest(user_id)
        return

    # offer_item = [{"itemName": "Carrot", "quantity": 1}]
    if item_present:
        recive_item = [{"itemName": quest_handler.stake_item, "quantity": 1}]
        offer_item = []

        ah = bag_instance.make_offer(
            target_identity_id=user_id,
            offer_to_give=offer_item,
            offer_to_receive=recive_item,
            callback_url=f"https://e9b2-49-36-33-127.ngrok-free.app/{user_id}",
        )
        max_wait = 60
        # print(quest_handler.approved)
        for i in range(max_wait // 6):
            quest_handler = Running_Quests[user_id]
            if quest_handler.approved:
                break
            await asyncio.sleep(10)

        if quest_handler.approved is False:
            await quest_handler.say_threaded("Quest Failed!")
            await end_quest(user_id)
            return
        else:
            return_val = bag_instance.make_offer(
                target_identity_id=user_id,
                offer_to_give=recive_item,
                offer_to_receive=offer_item,
            )
        print(return_val)
        await quest_handler.say_threaded("Quest Complete!")
        await end_quest(user_id)
        return


async def end_quest(user_id):
    Running_Quests.pop(user_id)
    # print(f"Ended quest for {user_id}")
    return


@app.event("app_mention")
async def event_test(event, say):
    await say(f"Hi there, <@{event['user']}>! use /bq-start to start a quest =)")


async def ack_shortcut(ack):
    await ack()


async def main():
    handler = AsyncSocketModeHandler(app, os.environ["SLACK_APP_TOKEN"])
    await handler.start_async()


# def start_webserver():
#     global Running_Quests
#     from robyn import Robyn

#     webserver = Robyn(__file__)

#     @webserver.post("/:user_id")
#     async def h(request):
#         global Running_Quests
#         user_id = request.path_params["user_id"]
#         print(Running_Quests)
#         Running_Quests[user_id].approved = True
#         # print(Running_Quests)
#         print(f"Approved {user_id}")
#         # print(user_id)
#         return {
#             "description": "Request received",
#             "status_code": 200,
#         }

#     webserver.start(port=8080)


if __name__ == "__main__":
    # manager = Manager()
    # Running_Quests = manager.dict()
    # load_quests()
    try:
        # p2 = Process(target=start_webserver, name="Webserver")
        # p2.start()
        # p1 = Process(target=asyncio.run(main()))
        # p1.start()
        asyncio.run(main())

        # TODO: Add a resouce usage monitor

    except KeyboardInterrupt:
        p2.join()
        p2.close()
        # p1.close()
        # raise SystemExit
        print("Exiting")

    finally:
        quests = [quest.to_dict() for quest in Running_Quests.values()]
        with open("quests.json", "w") as f:
            json.dump(quests, f)
        del quests
