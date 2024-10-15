from rtc.peer_connection import CustomRTCPeerConnection
import asyncio
from camera.camera_config import CameraState

class ConnectionManager:
    def __init__(self, appstate):
        self.connection_queue: asyncio.Queue = asyncio.Queue()
        self.appstate = appstate
     
    # Cameras Methods
    async def queue_camera_connection(self, peer_connection: CustomRTCPeerConnection, camera_id: str):          
        self.connection_queue.put((peer_connection, camera_id))
        if peer_connection:
            await peer_connection.connection_complete.wait()

    async def connect_peer_to_camera(self, peer_connection: CustomRTCPeerConnection, camera_id: str):
        camera = self.appstate.cameras[camera_id]
    
        if camera.state == CameraState.OFFLINE:
            await camera.start()

        if camera.state == CameraState.ONLINE:
            camera.clients += 1
            track = camera.relay.subscribe(camera.player)
            peer_connection.addTrack(track)
            peer_connection.connection_complete.set()
            
            if peer_connection.client_id not in self.appstate.client_camera_connections:
                self.appstate.client_camera_connections[peer_connection.client_id] = []
            self.appstate.client_camera_connections[peer_connection.client_id].append(camera_id)
        else:
            # Handle error: camera failed to start
            peer_connection.connection_complete.set()  # Set to allow client to receive error message

    async def disconnect_client_from_camera(self, client_id: str, camera_id: str):
        camera = self.appstate.cameras[camera_id]
        camera.clients -= 1
        
        if camera.clients == 0:
            await camera.stop()
        
    # Connection Processing 
    async def process_connections(self):
        while True:
            try:
                peer_connection, camera_id = await self.connection_queue.get()                
                camera = self.cameras.get(camera_id)
                
                if camera:
                    await self.connect_peer_to_camera(peer_connection, camera_id)
                else:
                    pass
                self.connection_queue.task_done()
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(e)
