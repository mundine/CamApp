# Standard library imports

# Third-party imports
from aiohttp import web
from aiortc import RTCSessionDescription

# Local application imports
from app.app import App
from .peer_connection import CustomRTCPeerConnection

def create_offer_handler(app: App):
    async def offer(request):
        params = await request.json()
        pc = CustomRTCPeerConnection()
        stream = params.get('stream')
        client_id = params.get('client')
        
        await app.add_client(client_id, pc)
        if stream:
            try:
                await app.connect_client_to_camera(client_id, stream)
            except ValueError as e:
                # Log the error or handle it appropriately
                print(e)
                pass
        
        await pc.setRemoteDescription(RTCSessionDescription(sdp=params["sdp"], type=params["type"]))
        answer = await pc.createAnswer()
        await pc.setLocalDescription(answer)
        
        return web.json_response({
            "sdp": pc.localDescription.sdp,
            "type": pc.localDescription.type
        })
    
    return offer
