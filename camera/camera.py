# Standard Library Imports
from typing import Optional, Dict, Set
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
from rtc.peer_connection import CustomRTCPeerConnection
class Camera:
    """
    Represents a camera with its configuration and state.
    Manages the camera's lifecycle, including starting and stopping the stream.
    """
    def __init__(self, camera_name: str, camera_data: Dict[str, str]):
        self.name = camera_name
        self.config = CameraConfig.from_dict(camera_data)
        self.state = CameraState.OFFLINE
        self.player: Optional[MediaStreamTrack] = None
        self.relay: Optional[MediaRelay] = None
        self.clients: Set[CustomRTCPeerConnection] = set()
        self.controller: Optional[CameraController] = None

    async def start(self):
        """
        Starts the camera stream and initializes the media player.
        """
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
            await self._handle_error("Timeout while connecting to camera")
        except av.error.ExitError as e:
            await self._handle_error(f"ExitError: {str(e)}")
        except Exception as e:
            await self._handle_error(f"Unexpected error: {str(e)}")

    async def stop(self):
        """
        Stops the camera stream and releases resources.
        """
        self.state = CameraState.OFFLINE
        if self.player:
            await asyncio.to_thread(self.player.stop)
        self.player = None
        self.relay = None
        self.controller = None

    async def check_health(self):
        """
        Checks the health of the camera by attempting to connect to its RTSP stream.
        Updates the camera state based on the connection result.
        Intended to prevent clients from trying to connect to an unavailable camera. 
        """
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

    async def _handle_error(self, error_message):
        logging.error(f"{self.name}: {error_message}")
        await self.stop()
        self.state = CameraState.UNAVAILABLE
