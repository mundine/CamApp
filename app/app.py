# Standard Library Imports
from typing import Dict

# Third Party Imports
import asyncio

# Local Application Imports
from camera.camera import Camera
from client.client import Client
from rtc.peer_connection import CustomRTCPeerConnection


class App:
    def __init__(self) -> None:
        self.cameras: Dict[str, Camera] = {}
        self.clients: Dict[str, Client] = {}
        self.connection_queue: asyncio.Queue = asyncio.Queue()
        self.status_data: dict = {}


    async def add_camera(self, camera_name, camera_data):
        self.cameras[camera_name] = Camera(camera_name, camera_data)
    

    async def add_client(self, client_id: str, peer_connection: CustomRTCPeerConnection):
        client = Client(peer_connection)
        self.clients[client_id] = client
        return client

    async def remove_client(self, client_id: str):
        client = self.clients.get(client_id)
        if client:
            for camera in self.cameras.values():
                await camera.remove_client(client)
            await client.peer_connection.close()
            del self.clients[client_id]

    async def connect_client_to_camera(self, client_id: str, camera_id: str):
        await self.connection_queue.put((client_id, camera_id))
        client = self.clients.get(client_id)
        if client:
            await client.connection_complete.wait()

    async def process_connections(self):
        while True:
            client_id, camera_id = await self.connection_queue.get()
            client = self.clients.get(client_id)
            camera = self.cameras.get(camera_id)
            if client and camera:
                await camera.add_client(client)
                client.connection_complete.set()
            else:
                pass # TODO: Handle this case
            self.connection_queue.task_done()

    async def disconnect_client_from_camera(self, client_id: str, camera_id: str):
        client = self.clients.get(client_id)
        camera = self.cameras.get(camera_id)
        if client and camera:
            await camera.remove_client(client)
        else:
            raise ValueError(f"Client {client_id} or Camera {camera_id} not found")
