# Standard Library Imports
from typing import Optional, Set, Dict
from concurrent.futures import ThreadPoolExecutor

#Third Party Imports    
from aiortc import MediaStreamTrack
from aiortc.contrib.media import MediaRelay, MediaPlayer
import asyncio
import av

#Local Application Imports
from client.client import Client
from controller.controller import CameraController
from camera.cameraconfig import CameraConfig, CameraState  

class Camera:
    def __init__(self, camera_name: str, camera_data: Dict[str, str]):
        self.name = camera_name
        self.config = CameraConfig.from_dict(camera_data)
        self.state = CameraState.OFFLINE
        self.player: Optional[MediaStreamTrack] = None
        self.relay: Optional[MediaRelay] = None
        self.connected_clients: Set[Client] = set()
        self.executor: ThreadPoolExecutor = ThreadPoolExecutor(max_workers=5)
        self.controller: Optional[CameraController] = None

    async def start(self):
        try:
            player = await asyncio.to_thread(MediaPlayer, self.config.rtsp_url, format="rtsp", timeout=5)
            self.player = player.video
            self.relay = MediaRelay()
            self.state = CameraState.ONLINE
            self.controller = CameraController(self.config)
        except av.error.ExitError: 
            await self.stop()
            self.state = CameraState.UNAVAILABLE

    async def stop(self):
        if self.player:
            await asyncio.to_thread(self.player.stop)
        self.player = None
        self.relay = None
        self.controller = None
        self.state = CameraState.OFFLINE

    async def add_client(self, client: Client):
        self.connected_clients.add(client)
        if len(self.connected_clients) == 1:
            await self.start()

    async def remove_client(self, client: Client):
        self.connected_clients.remove(client)
        if len(self.connected_clients) == 0:
            await self.stop()

    async def __aenter__(self):
        await self.start()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.stop()
