# Standard Library Imports
import asyncio
from typing import Set

# Local Application Imports
from rtc.peer_connection import CustomRTCPeerConnection
from utils.logger import get_logger


logger = get_logger(__name__)

#Clients will now only be CustomRTCPeerConnections. 
class ClientManager:
    """
    Manages connected clients, including adding, removing, and sending messages.
    """
    def __init__(self, appstate):
        self.appstate = appstate
        self.clients: Set[CustomRTCPeerConnection] = set()

    async def add_client(self, client: CustomRTCPeerConnection):
        """
        Adds a new client to the manager.

        :param client: The client to add.
        """
        self.clients.add(client)

    async def remove_client(self, client: CustomRTCPeerConnection):
        """
        Removes a new client from the manager.

        :param client: The client to remove.
        """
        try:
            self.clients.remove(client) 
        except Exception as e:
            logger.error(f"Failed to remove client {client.client_id}: {str(e)}")

    async def send_message_to_client(self, client: CustomRTCPeerConnection, message: str):
        """
        Sends a message to a specific client.

        :param client: The client to send the message to.
        :param message: The message to send.
        """
        try:
            client.datachannel.send(message)
        except Exception as e:
            logger.error(f"Failed to send message to client {client.client_id}: {str(e)}")


    async def send_message_to_all_clients(self, message: str):
        """
        Sends a message to all connected clients.

        :param message: The message to send.
        """
        tasks = []
        for client in self.clients:
            tasks.append(self.send_message_to_client(client, message))
        await asyncio.gather(*tasks)


    # Unused but potentially useful funcs
    async def get_client_list(self):
        return list(self.clients)

    async def get_client_count(self):
        return len(self.clients)

    async def get_client_by_camera_id(self, camera_id: str):
        return [client for client in self.clients if camera_id == client.camera_id]
