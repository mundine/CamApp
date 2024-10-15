# Standard library imports
import uuid
import json

# Third-party imports
from aiohttp import web
from aiortc import RTCSessionDescription

# Local application imports
from app_state import AppState
from .peer_connection import CustomRTCPeerConnection

def create_offer_handler(app: AppState):
    async def offer(request):
        params = await request.json()
        pc = CustomRTCPeerConnection()
        pc.client_id = str(uuid.uuid4())
        stream = params.get('stream')
        print(stream)
        if stream:
            try:
                await app.connection_manager.connect_peer_to_camera(pc, stream)
            except ValueError as e:
                pass
        
        await pc.setRemoteDescription(RTCSessionDescription(sdp=params["sdp"], type=params["type"]))
        answer = await pc.createAnswer()
        await pc.setLocalDescription(answer)
        
        @pc.on("connectionstatechange")
        async def on_connectionstatechange():
            print(pc.connectionState)
            if pc.connectionState == "connected":
                await app.add_client(pc)
            elif pc.connectionState in ["closed", "failed", "disconnected"]:
                await app.remove_client(pc)
    
        @pc.on("datachannel")
        async def on_datachannel(channel):
            client = app.clients[pc.client_id]
            client.datachannel = channel
            await app.send_initial_data(client)

            @channel.on("message")
            def on_message(message):
                try:
                    data = json.loads(message)
                    print(data)
                    if data['type'] == 'ptz':
                        print("hello?")
                        app.cameras[data['active_camera']].controller.handle_ptz_command(data, pc)
                except json.JSONDecodeError:
                    print("Error decoding message")

        return web.json_response({
            "sdp": pc.localDescription.sdp,
            "type": pc.localDescription.type
        })
    
    return offer
