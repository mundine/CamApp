# Standard Library Imports
from typing import Optional, Dict
from concurrent.futures import ThreadPoolExecutor
import asyncio
import socket
import av
import logging
from urllib.parse import urlparse

#Third Party Imports    
from aiortc import MediaStreamTrack
from aiortc.contrib.media import MediaRelay, MediaPlayer

#Local Application Imports
from controller.controller import CameraController
from camera.camera_config import CameraConfig, CameraState  

class Camera:
    def __init__(self, camera_name: str, camera_data: Dict[str, str]):
        self.name = camera_name
        self.config = CameraConfig.from_dict(camera_data)
        self.state = CameraState.OFFLINE
        self.player: Optional[MediaStreamTrack] = None
        self.relay: Optional[MediaRelay] = None
        self.clients: int = 0
        self.executor: ThreadPoolExecutor = ThreadPoolExecutor(max_workers=5)
        self.controller: Optional[CameraController] = None

    async def start(self):
        try:
            player = await asyncio.wait_for(
                asyncio.to_thread(MediaPlayer, self.config.rtsp_url, format="rtsp"),
                timeout=10
            )
            self.player = player.video
            self.relay = MediaRelay()
            self.state = CameraState.ONLINE
            self.controller = CameraController(self.config)
        except asyncio.TimeoutError:
            logging.error(f"Timeout while connecting to camera {self.name}")
            self.state = CameraState.UNAVAILABLE
        except av.error.ExitError as e:
            logging.error(f"ExitError for camera {self.name}: {str(e)}")
            await self.stop()
            self.state = CameraState.UNAVAILABLE
        except Exception as e:
            logging.error(f"Unexpected error starting camera {self.name}: {str(e)}")
            await self.stop()
            self.state = CameraState.UNAVAILABLE

    async def stop(self):
        self.state = CameraState.OFFLINE
        if self.player:
            await asyncio.to_thread(self.player.stop)
        self.player = None
        self.relay = None
        self.controller = None

    async def check_health(self):
            parsed_url = urlparse(self.config.rtsp_url)
            host = parsed_url.hostname
            port = parsed_url.port or 554
            
            try:
                _, _ = await asyncio.wait_for(
                    asyncio.open_connection(host, port),
                    timeout=1.0
                )
                self.state = CameraState.OFFLINE
            except (asyncio.TimeoutError, ConnectionRefusedError, socket.gaierror):
                self.state = CameraState.UNAVAILABLE
   

    async def __aenter__(self):
        await self.start()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.stop()
