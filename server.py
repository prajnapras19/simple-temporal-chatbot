import asyncio
from temporalio.client import Client
import websockets
import uuid


next_client_id = 1
clients = {}

async def handle_client(websocket, path):
    source_client_id = None
    if path.startswith("/bot"):
        query_string = path.split("?")[1]
        query_params = query_string.split("&")
        source_client_id = query_params[0].split("=")[1]

    global next_client_id
    client_id = uuid.uuid4()

    clients[client_id] = websocket
    print(f"Client {client_id} connected.")
    workflow_id = f"chat-workflow-{client_id}"

    try:
        while True:
            message = await websocket.recv()
            print(f"Received message from client {client_id}: {message}")

            if source_client_id:
                ws_client = None
                for c in clients.keys():
                    if str(c) == source_client_id:
                        ws_client = clients.get(c)
                        break
                if ws_client:
                    await ws_client.send(f"{message}")
            else:
                client = await Client.connect("localhost:7233")
                await client.start_workflow(
                        "chat-workflow",
                        client_id,
                        id=workflow_id,
                        task_queue="chatbot-task-queue",
                        start_signal="receive_message",
                        start_signal_args=[message]
                    )
    except websockets.exceptions.ConnectionClosedOK:
        del clients[client_id]
        print(f"Client {client_id} connection closed.")

async def start_server():
    async with websockets.serve(handle_client, "localhost", 8765):
        print("Server started. Listening on port 8765...")
        await asyncio.Future()

asyncio.run(start_server())

