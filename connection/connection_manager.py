from rtc.peer_connection import CustomRTCPeerConnection
import asyncio
import logging
from camera.camera_config import CameraState


class ConnectionManager:
    def __init__(self, appstate):
        self.connection_queue: asyncio.Queue = asyncio.Queue()
        self.appstate = appstate
        self.logger = logging.getLogger(__name__)
    
    async def queue_camera_connection(self, peer_connection: CustomRTCPeerConnection):          
        await self.connection_queue.put((peer_connection))
        if peer_connection:
            await peer_connection.connection_complete.wait()

    async def connect_client_to_camera(self, peer_connection: CustomRTCPeerConnection):
        camera_id = peer_connection.camera_id
        camera = self.appstate.camera_manager.cameras[camera_id]
    
        start_time = asyncio.get_event_loop().time()
        self.logger.info(f"Starting connection process for camera {camera_id}")

        if camera.state == CameraState.OFFLINE:
            camera_start_task = asyncio.create_task(camera.start())
        else:
            camera_start_task = None

        if camera.state == CameraState.ONLINE or camera_start_task:
            try:
                async with asyncio.timeout(10):  # 10-second timeout
                    if camera_start_task:
                        await camera_start_task
                    
                    track = await asyncio.to_thread(camera.relay.subscribe, camera.player)
                    print(camera.config)
                    peer_connection.addTrack(track)
                    peer_connection.connection_complete.set()
                    
                    end_time = asyncio.get_event_loop().time()
                    self.logger.info(f"Connection process for camera {camera_id} completed in {end_time - start_time:.2f} seconds")
            except asyncio.TimeoutError:
                self.logger.error(f"Connection process for camera {camera_id} timed out")
                peer_connection.connection_complete.set()  # Set to allow client to receive error message
        else:
            self.logger.error(f"Failed to connect to camera {camera_id}: Camera is not in ONLINE state")
            peer_connection.connection_complete.set()  # Set to allow client to receive error message
            
    # Connection Processing 
    async def process_connections(self):
        while True:
            try:
                peer_connection = await self.connection_queue.get()
                
                if peer_connection:
                    # Create a task for each connection request
                    asyncio.create_task(self.connect_client_to_camera(peer_connection))
                else:
                    pass
                self.connection_queue.task_done()
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error processing connection: {e}")
