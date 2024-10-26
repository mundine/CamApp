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
from utils.logger import get_logger

logger = get_logger(__name__)

def create_offer_handler(app: AppState):
    async def offer(request):
        params = await request.json()
        pc = CustomRTCPeerConnection()
        pc.client_id = str(uuid.uuid4())
        pc.camera_id = params.get('stream')

        @pc.on("connectionstatechange")
        async def on_connectionstatechange():
            logger.info(f"Connection state changed to: {pc.connectionState}")
            if pc.connectionState == "connected":
                await app.client_manager.add_client(pc)
                if pc.camera_id:
                    app.camera_manager.cameras[pc.camera_id].clients.add(pc)
                
            elif pc.connectionState in ["closed", "failed", "disconnected"]:
                await app.client_manager.remove_client(pc)
                if pc.camera_id:
                    try:
                        app.camera_manager.cameras[pc.camera_id].clients.remove(pc)
                    except Exception as e:
                        logger.error(f"Error removing client {pc.client_id} from camera {pc.camera_id}: {str(e)}")
                    
        @pc.on("datachannel")
        async def on_datachannel(channel):
            pc.datachannel = channel
            asyncio.create_task(app.send_initial_data(pc))

            @channel.on("message")
            def on_message(message):
                try:
                    data = json.loads(message)
                    logger.info(f"Received message: {data}")
                    if data['type'] == 'ptz':
                        result = app.camera_manager.cameras[data['camera']].controller.handle_ptz_command(data)
                        if result:
                            channel.send(json.dumps(result))
                        
                except json.JSONDecodeError:
                    logger.error("Error decoding message")

        if pc.camera_id:
            try:
                await app.connection_manager.queue_camera_connection(pc)
            except ValueError as e:
                logger.error(f"Error connecting to camera: {e}")
        
        await pc.setRemoteDescription(RTCSessionDescription(sdp=params["sdp"], type=params["type"]))
        answer = await pc.createAnswer()
        await pc.setLocalDescription(answer)
        
        return web.json_response({
            "sdp": pc.localDescription.sdp,
            "type": pc.localDescription.type
        })
    
    return offer
