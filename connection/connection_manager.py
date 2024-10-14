from camera.camera import Camera
from typing import Dict, List
from client.client import ClientData
from rtc.peer_connection import CustomRTCPeerConnection
import asyncio
from camera.camera_config import CameraState

class ConnectionManager:
    def  __init__(self):
        self.cameras: Dict[str, Camera] = {}
        self.clients: Dict[str, ClientData] = {}
        self.client_camera_connections: Dict[str, List[str]] = {}  # Client ID to list of Camera IDs
        self.connection_queue: asyncio.Queue = asyncio.Queue()
    
    # Client Methods

    async def add_client(self, peer_connection: CustomRTCPeerConnection):
        self.clients[peer_connection.client_id] = ClientData(peer_connection)

    async def remove_client(self, peer_connection: CustomRTCPeerConnection):
        client_id = peer_connection.client_id
        if client_id in self.client_camera_connections:
            camera_ids = self.client_camera_connections[client_id]
            for camera_id in camera_ids:
                await self.disconnect_client_from_camera(client_id, camera_id)    
            del self.client_camera_connections[client_id]
        
        if client_id in self.clients:
            del self.clients[client_id]
            
    # Cameras Methods

    async def add_camera(self, camera_id: str, camera: Camera):
        self.cameras[camera_id] = Camera(camera_id, camera)

    async def queue_camera_connection(self, peer_connection: CustomRTCPeerConnection, camera_id: str):          
        self.connection_queue.put((peer_connection, camera_id))
        if peer_connection:
            await peer_connection.connection_complete.wait()

    async def connect_peer_to_camera(self, peer_connection: CustomRTCPeerConnection, camera_id: str):
        camera = self.cameras[camera_id]
    
        if camera.state == CameraState.OFFLINE:
            await camera.start()

        if camera.state == CameraState.ONLINE:
            camera.clients += 1
            track = camera.relay.subscribe(camera.player)
            peer_connection.addTrack(track)
            peer_connection.connection_complete.set()
            
            if peer_connection.client_id not in self.client_camera_connections:
                self.client_camera_connections[peer_connection.client_id] = []
            self.client_camera_connections[peer_connection.client_id].append(camera_id)
        else:
            # Handle error: camera failed to start
            peer_connection.connection_complete.set()  # Set to allow client to receive error message

    async def camera_health_check(self, camera_id: str):
        #Check if self.client_camera_connections for active connections
        #If no active connections, stop camera
        #If camera is offline, run health check (TODO)
        #Set status
        pass
        
    async def disconnect_client_from_camera(self, client_id: str, camera_id: str):
        camera = self.cameras[camera_id]
        camera.clients -= 1
        
        if camera.clients == 0:
            await camera.stop()
        
    def get_connected_camera(self, client: str) -> str:
        pass

    def get_connected_clients(self, camera_id: str) -> List[str]:
        pass

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
