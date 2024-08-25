import os
import json

from bag import bag_instance

from slack_bolt.app.async_app import AsyncApp
from slack_bolt.adapter.socket_mode.async_handler import AsyncSocketModeHandler

app = AsyncApp(token=os.environ["SLACK_BOT_TOKEN"])

bag_instance.configure(
    int(os.environ["BAG_ID"]), os.environ["BAG_TOKEN"], os.environ["QUEST_OWNER_ID"]
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
        # await quest_handler.say_threaded(f"{bag_instance.get_inventory(user_id)}")
    return


@app.command("/bq-wipe")
async def clear_pending(ack, body, respond):
    user_id = body["user_id"]
    if user_id != os.environ["QUEST_OWNER_ID"]:
        await ack()
        await respond(
            f"Hey <@{user_id}>, only the owner can interact with the options."
        )
        return
    else:
        n = len(Running_Quests)
        Running_Quests.clear()
        await ack()
        # with open("quests.json", "w") as f:
        #     json.dump([], f)
        await respond(f"Wiped {n} quests")


@app.action("static_select-action")
async def handle_some_action(ack, body, logger, say, respond):
    user_id = body["user"]["id"]
    # print(user_id , type(user_id))
    try:
        quest_handler = Running_Quests[user_id]
    except KeyError:
        await ack()
        await respond(
            f"Hey <@{user_id}>, You have already chosen an item or all quests have been wiped."
        )
        return
    # print(Running_Quests)
    if user_id != quest_handler.user_id:
        await ack()
        await respond(
            f"Hey <@{user_id}>, only the quest owner can interact with the options."
        )
        return

    # if user_id not in Running_Quests.keys():
    #     await ack()
    #     await respond(f"Hey <@{user_id}>, You have already chosen an item.")
    #     return
    # print()
    # quest_handler.ping_user = None
    # print(Running_Quests[user_id].ping_user) # WOA PYTHON SYNCS STATES

    await ack()
    selected_option = body["actions"][0]["selected_option"]
    await quest_handler.say_threaded(
        f"You have selected {selected_option['text']['text']}", say
    )
    quest_handler.stake_item = selected_option["text"]["text"].split(" ")[-1]
    inv = bag_instance.get_inventory("U07HEB24LCC")
    print(inv)

    #     message OfferItem {
    #   optional string itemName = 1;
    #   optional int32 quantity = 2;
    # }
    print(quest_handler.stake_item)
    offer_item = {'itemName': quest_handler.stake_item, 'quantity': 1}
    # print(offer_item)

    # def make_offer(self, target_identity_id: str, offer_to_give: RCFContainer[bag_pb2.OfferItem], offer_to_receive: RCFContainer[bag_pb2.OfferItem]):
    #     if self.stub is None:
    #         raise ValueError("BagManager not configured. Call bm_instance.configure() first.")
    #     result = self.stub.MakeOffer(bag_pb2.MakeOfferRequest(appId=self.app_id, key=self.key, sourceIdentityId=self.owner_id, ))

    bag_instance.make_offer(target_identity_id=user_id, offer_to_give=offer_item, offer_to_receive=offer_item)

    # print(quest_handler.stake_item)
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


if __name__ == "__main__":
    import asyncio

    try:
        asyncio.run(main())
        # TODO: Add a resouce usage monitor
    except KeyboardInterrupt:
        print("Exiting")
    finally:
        quests = [quest.to_dict() for quest in Running_Quests.values()]
        with open("quests.json", "w") as f:
            json.dump(quests, f)
        del quests
