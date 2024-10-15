# Standard library imports
import uuid
import json
import asyncio

# Third-party imports
from aiohttp import web
from aiortc import RTCSessionDescription

# Local application imports
from app_state import AppState
from .peer_connection import CustomRTCPeerConnection
from camera.camera import Camera

def create_offer_handler(app: AppState):
    async def offer(request):
        params = await request.json()
        pc = CustomRTCPeerConnection()
        pc.client_id = str(uuid.uuid4())

        @pc.on("connectionstatechange")
        async def on_connectionstatechange():
            print(f"Connection state changed to: {pc.connectionState}")
            if pc.connectionState == "connected":
                await app.add_client(pc)
                
            elif pc.connectionState in ["closed", "failed", "disconnected"]:
                await app.remove_client(pc)
        
        @pc.on("datachannel")
        async def on_datachannel(channel):
            client = app.clients[pc.client_id]
            client.datachannel = channel
            asyncio.create_task(app.send_initial_data(client))

            @channel.on("message")
            def on_message(message):
                try:
                    data = json.loads(message)
                    print(f"Received message: {data}")
                    if data['type'] == 'ptz':
                        client = app.clients[pc.client_id]
                        app.cameras[data['camera']].controller.handle_ptz_command(data, client)
                        
                except json.JSONDecodeError:
                    print("Error decoding message")
                            
        stream = params.get('stream')
        print(f"Requested stream: {stream}")

        if stream:
            try:
                await app.connection_manager.connect_peer_to_camera(pc, stream)
            except ValueError as e:
                print(f"Error connecting to camera: {e}")
        
        await pc.setRemoteDescription(RTCSessionDescription(sdp=params["sdp"], type=params["type"]))
        answer = await pc.createAnswer()
        await pc.setLocalDescription(answer)
        
        return web.json_response({
            "sdp": pc.localDescription.sdp,
            "type": pc.localDescription.type
        })
    
    return offer
