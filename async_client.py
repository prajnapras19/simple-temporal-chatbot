import asyncio
import websockets
from prompt_toolkit import prompt

async def receive_messages(websocket):
    try:
        while True:
            message = await websocket.recv()
            print(f"\n{'':<60}{message}")
    except websockets.exceptions.ConnectionClosedOK:
        print("\nWebSocket connection closed.")

async def send_user_input(websocket):
    while True:
        user_input = await asyncio.to_thread(prompt, "")

        await websocket.send(user_input)

async def main():
    uri = "ws://localhost:8765"
    async with websockets.connect(uri) as websocket:
        receive_task = asyncio.create_task(receive_messages(websocket))
        send_task = asyncio.create_task(send_user_input(websocket))

        await asyncio.gather(receive_task, send_task)

if __name__ == "__main__":
    asyncio.run(main())

