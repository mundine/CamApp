# Standard Library Imports
from typing import Dict
import gc

# Third Party Imports
import asyncio

# Local Application Imports
from camera.camera import Camera
from client.client import ClientData
from rtc.peer_connection import CustomRTCPeerConnection
from utils.logger import get_logger

# Import Logger
logger = get_logger(__name__)


class App:
    def __init__(self) -> None:
        self.cameras: Dict[str, Camera] = {}
        self.clients: Dict[str, ClientData] = {}
        self.connection_queue: asyncio.Queue = asyncio.Queue()
        self.status_data: dict = {}


    async def add_camera(self, camera_name, camera_data):
        self.cameras[camera_name] = Camera(camera_name, camera_data)
    

    async def add_client(self, peer_connection: CustomRTCPeerConnection):
        client_id = peer_connection.client_id
        self.clients[client_id] = ClientData(peer_connection)
        logger.info(f'Client Added, Total Clients: {len(self.clients)}')

    async def remove_client(self, peer_connection: CustomRTCPeerConnection):        
        client_id = peer_connection.client_id
        if client_id in self.clients:
            client = self.clients[client_id]
            logger.info(f"Removing client {client.peer_connection}")
            for camera in self.cameras.values():
                if client.peer_connection in camera.connected_clients:
                    await camera.remove_client(client.peer_connection)
            await client.peer_connection.close()
            del self.clients[client_id]
            logger.info(f"Client removed. Total clients: {len(self.clients)}")
        else:
            logger.warning(f"Attempted to remove non-existent client {peer_connection}")
        gc.collect()

    async def connect_peer_to_camera(self, peer_connection: CustomRTCPeerConnection, camera_id: str):
        camera = self.cameras.get(camera_id)
        if camera:
            logger.info(f"Connecting client {peer_connection.client_id} to camera {camera_id}")
            await camera.add_client(peer_connection)
            peer_connection.connection_complete.set()
        else:
            logger.warning(f"Failed to connect: Camera {camera_id} not found")
            peer_connection.connection_complete.set()

    

    async def process_connections(self):
        logger.info("Starting process_connections task")
        while True:
            try:
                logger.debug("Waiting for connection in queue")
                peer_connection, camera_id = await self.connection_queue.get()
                logger.info(f"Processing connection: Client {peer_connection} to Camera {camera_id}")
                
                camera = self.cameras.get(camera_id)
                
                if camera:
                    logger.info(f"Connecting client {peer_connection} to camera {camera_id}")
                    await camera.add_client(peer_connection)
                    peer_connection.connection_complete.set()
                else:
                    logger.warning(f"Failed to connect: Client or Camera {camera_id} not found")
                
                self.connection_queue.task_done()
            except asyncio.CancelledError:
                logger.info("process_connections task cancelled")
                break
            except Exception as e:
                logger.error(f"Error in process_connections: {str(e)}")

    
