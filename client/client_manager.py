#Manage Clients
from rtc.peer_connection import CustomRTCPeerConnection
from typing import Set
from utils.logger import get_logger
import asyncio

logger = get_logger(__name__)

#Clients will now only be CustomRTCPeerConnections. 
class ClientManager:
    def __init__(self, appstate):
        self.appstate = appstate
        self.clients: Set[CustomRTCPeerConnection] = set()

    async def add_client(self, client: CustomRTCPeerConnection):
        self.clients.add(client)

    async def remove_client(self, client: CustomRTCPeerConnection):
        try:
            self.clients.remove(client) 
        except Exception as e:
            logger.error(f"Failed to remove client {client.client_id}: {str(e)}")

    async def send_message_to_client(self, client: CustomRTCPeerConnection, message: str):
        try:
            client.datachannel.send(message)
        except Exception as e:
            logger.error(f"Failed to send message to client {client.client_id}: {str(e)}")

    async def send_message_to_all_clients(self, message: str):
        tasks = []
        for client in self.clients:
            tasks.append(self.send_message_to_client(client, message))
        await asyncio.gather(*tasks)

    async def get_client_list(self):
        return list(self.clients)

    async def get_client_count(self):
        return len(self.clients)

    async def get_client_by_camera_id(self, camera_id: str):
        return [client for client in self.clients if camera_id == client.camera_id]
