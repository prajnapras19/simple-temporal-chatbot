from datetime import timedelta

from temporalio import activity, workflow
import websockets


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
        self.message = ""
        self.client_id = ""

    @workflow.run
    async def run(self, client_id: str) -> str:
        self.client_id = client_id
        message = "Welcome to chatbot. Type 'exit' to exit."
        await workflow.execute_activity(
            "bot_reply",
            args=[message, self.client_id],
            start_to_close_timeout=timedelta(seconds=10)
        )
        message = "What do you want to explore? core workflow or chatbot?"
        await workflow.execute_activity(
            "bot_reply",
            args=[message, self.client_id],
            start_to_close_timeout=timedelta(seconds=10)
        )
        self.message = ""
        is_completed = False
        while not is_completed:
            await workflow.wait_condition(
                lambda: not self.message == ""
            )

            if self.message == "core workflow":
                message = "This is a example of core workflow"
                await workflow.execute_activity(
                    "bot_reply",
                    args=[message, self.client_id],
                    start_to_close_timeout=timedelta(seconds=10)
                )
                self.message = ""
                is_completed = True
            elif self.message == "chatbot":
                message = "This is a example of chatbot"
                await workflow.execute_activity(
                    "bot_reply",
                    args=[message, self.client_id],
                    start_to_close_timeout=timedelta(seconds=10)
                )
                self.message = ""
                is_completed = True
            else:
                message = "I don't understand. Please type 'core workflow' or 'chatbot'"
                await workflow.execute_activity(
                    "bot_reply",
                    args=[message, self.client_id],
                    start_to_close_timeout=timedelta(seconds=10)
                )
                self.message = ""
        message = "That's all for now. Type 'exit' to exit."
        await workflow.execute_activity(
            "bot_reply",
            args=[message, self.client_id],
            start_to_close_timeout=timedelta(seconds=10)
        )

        self.message = ""
        is_completed = False
        while not is_completed:
            await workflow.wait_condition(
                lambda: not self.message == ""
            )

            if self.message == "exit":
                is_completed = True
            else:
                message = "I don't understand. Please type 'exit' to exit."
                await workflow.execute_activity(
                    "bot_reply",
                    args=[message, self.client_id],
                    start_to_close_timeout=timedelta(seconds=10)
                )
                self.message = ""

        message = "Thank you"
        await workflow.execute_activity(
            "bot_reply",
            args=[message, self.client_id],
            start_to_close_timeout=timedelta(seconds=10)
        )
        return "Chatbot completed"

    @workflow.signal
    def receive_message(self, message: str) -> None:
        self.message = message

