# # from aiohttp import web
# # import asyncio
# # import aiohttp_cors
# # from aiortc import RTCPeerConnection, RTCSessionDescription
# # from aiortc.contrib.media import MediaRelay, MediaPlayer



# # pcs = set()
# # relay = MediaRelay()

# # async def offer(request):
# #     params = await request.json()
# #     pc = RTCPeerConnection()


# #     pcs.add(pc)
# #     @pc.on("iceconnectionstatechange")
# #     def on_ice_state_change():
# #         print("ICE connection state is %s" % pc.iceConnectionState)
# #         if pc.iceConnectionState == "failed":
# #             asyncio.ensure_future(pc.close())
# #             pcs.discard(pc)

# #     @pc.on("track")
# #     def on_track(track):
# #         print("Received track: %s" % track.kind)
# #         if track.kind == "video":
# #             player = MediaPlayer("video=Integrated Camera", format="dshow")
# #             pc.addTrack(player.video)

# #     offer = RTCSessionDescription(sdp=params["sdp"], type=params["type"])
# #     await pc.setRemoteDescription(offer)


# #     answer = await pc.createAnswer()
# #     await pc.setLocalDescription(answer)

# #     while pc.iceGatheringState != "complete":
# #         await asyncio.sleep(0.1)

# #     return web.json_response({
# #         "sdp": pc.localDescription.sdp,
# #         "type": pc.localDescription.type
# #     })

# # app = web.Application()
# # cors = aiohttp_cors.setup(app, defaults={
# #     "*": aiohttp_cors.ResourceOptions(
# #         allow_credentials=True,
# #         expose_headers="*",
# #         allow_headers="*",
# #     )
# # })

# # # Add route and enable CORS on it
# # resource = cors.add(app.router.add_resource("/offer"))
# # cors.add(resource.add_route("POST", offer))


# # if __name__ == "__main__":
# #     web.run_app(app, port=8080)


# from aiohttp import web
# from flask import Flask ,render_template
# import asyncio
# import aiohttp_cors
# from aiortc import RTCPeerConnection, RTCSessionDescription
# from aiortc.contrib.media import MediaRelay, MediaPlayer

# pcs = set()

# async def offer(request):
#     params = await request.json()
#     pc = RTCPeerConnection()
#     pcs.add(pc)

#     print("Creating local media stream for callee...")
#     player = MediaPlayer('video=Integrated Camera', format='dshow')
 

#     # Add callee's media tracks to the connection
#     if player.audio:
#         pc.addTrack(player.audio)
#     if player.video:
#         pc.addTrack(player.video)

#     @pc.on("iceconnectionstatechange")
#     def on_ice_state_change():
#         print("ICE state is", pc.iceConnectionState)
#         if pc.iceConnectionState == "failed":
#             asyncio.ensure_future(pc.close())
#             pcs.discard(pc)

#     @pc.on("track")
#     def on_track(track):
#         print(f"Received track from caller: {track.kind}")

#     # Handle caller's offer
#     offer = RTCSessionDescription(sdp=params["sdp"], type=params["type"])
#     await pc.setRemoteDescription(offer)

#     # Create and send answer
#     answer = await pc.createAnswer()
#     await pc.setLocalDescription(answer)

#     while pc.iceGatheringState != "complete":
#         await asyncio.sleep(0.1)

#     return web.json_response({
#         "sdp": pc.localDescription.sdp,
#         "type": pc.localDescription.type
#     })


# # Web app setup
# app = web.Application()
# cors = aiohttp_cors.setup(app, defaults={
#     "*": aiohttp_cors.ResourceOptions(
#         allow_credentials=True,
#         expose_headers="*",
#         allow_headers="*",
#     )
# })

# resource = cors.add(app.router.add_resource("/offer"))
# cors.add(resource.add_route("POST", offer))

# if __name__ == "__main__":
#     web.run_app(app, port=8080)


import os
from aiohttp import web
import asyncio
import aiohttp_cors
from aiortc import RTCPeerConnection, RTCSessionDescription
from aiortc.contrib.media import MediaPlayer

pcs = set()
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

async def index(request):
    return web.FileResponse(os.path.join(BASE_DIR, "index.html"))

async def offer(request):
    try:
        params = await request.json()
        pc = RTCPeerConnection()
        pcs.add(pc)

        print("Creating local media stream for callee...")
        player = MediaPlayer('video=Integrated Camera', format='dshow')

        if player.audio:
            pc.addTrack(player.audio)
        if player.video:
            pc.addTrack(player.video)

        @pc.on("iceconnectionstatechange")
        def on_ice_state_change():
            print("ICE state is", pc.iceConnectionState)
            if pc.iceConnectionState == "failed":
                asyncio.ensure_future(pc.close())
                pcs.discard(pc)

        @pc.on("track")
        def on_track(track):
            print(f"Received track from caller: {track.kind}")

        offer = RTCSessionDescription(sdp=params["sdp"], type=params["type"])
        await pc.setRemoteDescription(offer)

        answer = await pc.createAnswer()
        await pc.setLocalDescription(answer)

        while pc.iceGatheringState != "complete":
            await asyncio.sleep(0.1)

        return web.json_response({
            "sdp": pc.localDescription.sdp,
            "type": pc.localDescription.type
        })
    except Exception as e:
        print("Error in /offer:", e)
        return web.Response(status=500, text="Server got itself in trouble")

app = web.Application()
cors = aiohttp_cors.setup(app, defaults={
    "*": aiohttp_cors.ResourceOptions(
        allow_credentials=True,
        expose_headers="*",
        allow_headers="*",
    )
})

app.router.add_get("/", index)  # serve index.html on /

resource = cors.add(app.router.add_resource("/offer"))
cors.add(resource.add_route("POST", offer))

if __name__ == "__main__":
    web.run_app(app, port=8080)



