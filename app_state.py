# Standard Library Imports
import asyncio
import json
from typing import Dict, List

# Local Application Imports
from camera.camera import Camera
from camera.camera_config import CameraState
from client.client import ClientData
from connection.connection_manager import ConnectionManager
from rtc.peer_connection import CustomRTCPeerConnection
from utils.logger import get_logger

logger = get_logger(__name__)

class AppState:
    def  __init__(self):
        self.cameras: Dict[str, Camera] = {}
        self.clients: Dict[str, ClientData] = {}
        self.client_camera_connections: Dict[str, List[str]] = {}  # Client ID to list of Camera IDs
        self.connection_manager: ConnectionManager = ConnectionManager(self)
        self.status_data: Dict = {}
        self.camera_data: List = []
        self.heartbeat_interval = 5  # seconds -> update to 60s when moving to production

    async def add_camera(self, camera_id: str, camera: Camera):
        self.cameras[camera_id] = Camera(camera_id, camera)
        self.camera_data.append(camera_id)
        
    async def add_client(self, peer_connection: CustomRTCPeerConnection):
            self.clients[peer_connection.client_id] = ClientData(peer_connection)

    async def remove_client(self, peer_connection: CustomRTCPeerConnection):
        client_id = peer_connection.client_id
        if client_id in self.client_camera_connections:
            camera_ids = self.client_camera_connections[client_id]
            for camera_id in camera_ids:
                await self.connection_manager.disconnect_client_from_camera(client_id, camera_id)    
            del self.client_camera_connections[client_id]
        
        if client_id in self.clients:
            del self.clients[client_id]

    async def update_status_data(self): 
        new_status_data = {}
        for camera_id, camera in self.cameras.items():
            if camera.state != CameraState.ONLINE:
                await camera.check_health()
            new_status_data[camera_id] = {
                'status': self.__get_camera_status(camera),
                'clients': camera.clients
            }
        
        if new_status_data != self.status_data:
            self.status_data = new_status_data
            await self.send_heartbeat_to_all_clients()

    def __get_camera_status(self, camera: Camera) -> str:
        return {
            CameraState.OFFLINE: 'Offline',
            CameraState.UNAVAILABLE: 'Unavailable',
            CameraState.ONLINE: 'Online'
        }.get(camera.state, 'Unknown')

    async def send_heartbeat_to_all_clients(self):
        heartbeat_message = json.dumps({'type': 'heartbeat', 'data': self.status_data})
        tasks = []
        for client in self.clients.values():
            tasks.append(self.send_message_to_client(client, heartbeat_message))
        await asyncio.gather(*tasks)

    async def send_message_to_client(self, client: ClientData, message: str):
        try:
            client.datachannel.send(message)
        except Exception as e:
            logger.error(f"Failed to send message to client {client.peer_connection.client_id}: {str(e)}")

    async def start_heartbeat(self):
        while True:
            await self.update_status_data()
            await asyncio.sleep(self.heartbeat_interval)

    async def send_initial_data(self, client: ClientData):
        camera_info_message = json.dumps({'type': 'camera_info', 'data': self.camera_data})
        heartbeat_message = json.dumps({'type': 'heartbeat', 'data': self.status_data})
        
        await asyncio.gather(
            self.send_message_to_client(client, camera_info_message),
            self.send_message_to_client(client, heartbeat_message)
        )
