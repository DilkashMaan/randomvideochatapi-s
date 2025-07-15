import os
import asyncio
from aiohttp import web
 
# Store all connected WebSocket clients
clients = set()
 
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
 
# Serve the index.html page
async def index(request):
    return web.FileResponse(os.path.join(BASE_DIR, "index.html"))
 
# WebSocket handler for signaling
async def websocket_handler(request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)
 
    clients.add(ws)
    print(f"Client connected: {len(clients)} total")
 
    try:
        async for msg in ws:
            if msg.type == web.WSMsgType.TEXT:
                # Relay message to all other connected clients
                for client in clients:
                    if client != ws:
                        await client.send_str(msg.data)
            elif msg.type == web.WSMsgType.ERROR:
                print(f'ws connection closed with exception {ws.exception()}')
    finally:
        clients.remove(ws)
        print(f"Client disconnected: {len(clients)} remaining")
 
    return ws
 
# Create app and routes
app = web.Application()
app.router.add_get("/", index)
app.router.add_get("/ws", websocket_handler)
 
# Run the app on port 8765
if __name__ == '__main__':
    web.run_app(app, port=8765)