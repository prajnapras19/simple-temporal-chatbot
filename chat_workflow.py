from datetime import timedelta
from temporalio import workflow, activity
import websockets
import chatbot_fsm

@activity.defn
async def bot_reply(message: "str", source_client_id: "str"):
    uri = f"ws://localhost:8765/bot?client_id={source_client_id}"
    async with websockets.connect(uri) as websocket:
        await websocket.send(message)
    await websocket.close()
    return message

@workflow.defn(name="chat-workflow")
class ChatWorkflow:
    def __init__(self) -> None:
        self.chat_parameter = chatbot_fsm.ChatParameter(chat_id="", message="")
        self.chatbot = chatbot_fsm.ChatbotFSM(self.chat_parameter)

    @workflow.run
    async def run(self, client_id: str) -> str:
        self.chat_parameter.chat_id = client_id

        await workflow.execute_activity(
            "bot_reply",
            args=[self.chatbot.reply, self.chat_parameter.chat_id],
            start_to_close_timeout=timedelta(seconds=10)
        )

        while not self.chatbot.is_completed:
            self.chat_parameter.message = ""
            await workflow.wait_condition(
                lambda: not self.chat_parameter.message == ""
            )
            
            is_transitioning = False
            for transition in self.chatbot.transitions:
                if transition['trigger'] == self.chat_parameter.message and transition['source'] == self.chatbot.state:
                    is_transitioning = True
                    self.chatbot.trigger(self.chat_parameter.message)

            if not is_transitioning:
                await workflow.execute_activity(
                    "bot_reply",
                    args=[self.chatbot.unrecognized_option_reply, self.chat_parameter.chat_id],
                    start_to_close_timeout=timedelta(seconds=10)
                )
            else:
                await workflow.execute_activity(
                    "bot_reply",
                    args=[self.chatbot.reply, self.chat_parameter.chat_id],
                    start_to_close_timeout=timedelta(seconds=10)
                )

        return "Chat completed"

    @workflow.signal
    def receive_message(self, message: str) -> None:
        self.chat_parameter.message = message

