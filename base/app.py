import asyncio
import websockets
from websockets.exceptions import ConnectionClosedOK, ConnectionClosedError, ConnectionClosed

connected = set()

async def handler(websocket):
    connected.add(websocket)
    print("A user connected")
    try:
        async for message in websocket:
            to_remove = set()
            for client in connected:
                if client != websocket:
                    try:
                        await client.send(message)
                    except ConnectionClosed:
                        to_remove.add(client)
            for c in to_remove:
                connected.remove(c)
    except ConnectionClosedOK:
        print("A user disconnected cleanly")
    except ConnectionClosedError:
        print("A user disconnected with error")
    finally:
        connected.remove(websocket)
        

async def main():
    async with websockets.serve(handler, "localhost", 8080):
        print("WebSocket server running on ws://localhost:8080")
        await asyncio.Future() 


if __name__ == "__main__":
    asyncio.run(main())
