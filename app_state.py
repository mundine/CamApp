# Standard Library Imports
import asyncio

# Local Application Imports
from connection.connection_manager import ConnectionManager
from rtc.peer_connection import CustomRTCPeerConnection
from utils.logger import get_logger
from client.client_manager import ClientManager
from camera.camera_manager import CameraManager

logger = get_logger(__name__)

class AppState:
    def  __init__(self):
        self.camera_manager: CameraManager = CameraManager(self)
        self.client_manager: ClientManager = ClientManager(self)
        self.connection_manager: ConnectionManager = ConnectionManager(self)
        self.heartbeat_interval = 60 #seconds
        self.last_heartbeat = 0  # Add this line to track the last heartbeat time

    async def start_heartbeat(self):
        while True:
            if self.last_heartbeat >= self.heartbeat_interval:
                await self.camera_manager.update_status_data()
                await self.client_manager.send_message_to_all_clients(self.camera_manager.camera_state)
                self.last_heartbeat = 0
            else:
                self.last_heartbeat += 1
            await asyncio.sleep(1)

    async def send_initial_data(self, client: CustomRTCPeerConnection):
        try:
            # Update status data before sending
            await self.camera_manager.update_status_data()
            
            # Reset the heartbeat timer
            self.last_heartbeat = 0

            # Send initial data to the client
            await self.client_manager.send_message_to_client(client, self.camera_manager.send_camera_names())
            await self.client_manager.send_message_to_client(client, self.camera_manager.camera_state)
        except Exception as e:
            logger.error(f"Error sending initial data to client {client.client_id}: {str(e)}")
