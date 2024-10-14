# Standard library imports
import uuid

# Third-party imports
from aiohttp import web
from aiortc import RTCSessionDescription

# Local application imports
from connection.connection_manager import ConnectionManager
from .peer_connection import CustomRTCPeerConnection

def create_offer_handler(app: ConnectionManager):
    async def offer(request):
        params = await request.json()
        pc = CustomRTCPeerConnection()
        pc.client_id = str(uuid.uuid4())
        stream = params.get('stream')

        if stream:
            try:
                await app.connect_peer_to_camera(pc, stream)
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
            app.clients[pc.client_id].datachannel = channel
            await app.send_camera_data(pc)
            await app.send_initial_status(pc)

        return web.json_response({
            "sdp": pc.localDescription.sdp,
            "type": pc.localDescription.type
        })
    
    return offer
