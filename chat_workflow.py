from datetime import timedelta
from temporalio import workflow, activity
import websockets
import blocks

class ChatParameter:
    def __init__(self, chat_id, message):
        self.chat_id = chat_id
        self.message = message

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
        self.chat_parameter = blocks.ChatParameter(chat_id="", message="")

    @workflow.run
    async def run(self, client_id: str) -> str:
        self.chat_parameter.chat_id = client_id
        self.dialog = blocks.DEFAULT_DIALOG

        i = 0
        current_keyword = None
        while i < len(self.dialog.actions):
            if isinstance(self.dialog.actions[i], blocks.TextReceiver):
                await workflow.wait_condition(
                    lambda: not self.chat_parameter.message == ""
                )
                self.dialog.actions[i].parameter.set_received_message(self.chat_parameter.message)
                current_keyword = self.dialog.actions[i].execute().get_output()
                i += 1
                self.chat_parameter.message = ""
            elif isinstance(self.dialog.actions[i], blocks.Branching):
                self.dialog.actions[i].parameter.condition_parameter = current_keyword
                
                action = self.dialog.actions[i].execute().get_output()
                while isinstance(action, blocks.Branching):
                    action.parameter.condition_parameter = current_keyword
                    action = action.execute().get_output()

                if isinstance(action, blocks.SendText):
                    action.parameter.generate_response_parameter = self.chat_parameter
                    action.execute()
                    await workflow.execute_activity(
                        "bot_reply",
                        args=[action.parameter.message, self.chat_parameter.chat_id],
                        start_to_close_timeout=timedelta(seconds=10)
                    )
                    i += 1
                elif isinstance(action, blocks.GoToDialog):
                    self.dialog = action.parameter.dialog
                    i = 0
                elif isinstance(self.dialog.actions[i], blocks.Script):
                    self.dialog.actions[i].parameter.function_parameter = [self.chat_parameter, current_keyword]
                    self.dialog.actions[i].execute()
                    i += 1
            elif isinstance(self.dialog.actions[i], blocks.SendText):
                self.dialog.actions[i].parameter.generate_response_parameter = self.chat_parameter
                self.dialog.actions[i].execute()
                await workflow.execute_activity(
                    "bot_reply",
                    args=[self.dialog.actions[i].parameter.message, self.chat_parameter.chat_id],
                    start_to_close_timeout=timedelta(seconds=10)
                )
                i += 1
            elif isinstance(self.dialog.actions[i], blocks.GoToDialog):
                self.dialog = self.dialog.actions[i].parameter.dialog
                i = 0
            elif isinstance(self.dialog.actions[i], blocks.Script):
                self.dialog.actions[i].parameter.function_parameter = [self.chat_parameter, current_keyword]
                self.dialog.actions[i].execute()
                i += 1

        return "Chat completed"

    @workflow.signal
    def receive_message(self, message: str) -> None:
        self.chat_parameter.message = message

