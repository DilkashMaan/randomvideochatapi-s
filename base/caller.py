import asyncio
import json
import aiohttp
from aiortc import RTCPeerConnection, RTCSessionDescription
from aiortc.contrib.media import MediaPlayer

async def run():
    pc = RTCPeerConnection()

    player = MediaPlayer('video=Camo', format='dshow')
  

    if player.audio:
        pc.addTrack(player.audio)
    if player.video:
        pc.addTrack(player.video)

    @pc.on("iceconnectionstatechange")
    def on_ice_state_change():
        print("ICE connection state:", pc.iceConnectionState)

    @pc.on("track")
    def on_track(track):
        print(f"Received track from callee: {track.kind}")

    offer = await pc.createOffer()
    await pc.setLocalDescription(offer)

    async with aiohttp.ClientSession() as session:
        async with session.post("http://127.0.0.1:8080/offer", json={
            "sdp": pc.localDescription.sdp,
            "type": pc.localDescription.type
        }) as resp:
            answer = await resp.json()

    await pc.setRemoteDescription(RTCSessionDescription(
        sdp=answer["sdp"],
        type=answer["type"]
    ))

    print("WebRTC connection established. Waiting for tracks...")

    while True:
        await asyncio.sleep(1)

if __name__ == "__main__":
    asyncio.run(run())
