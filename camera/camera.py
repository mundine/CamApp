
# Standard Library Imports
from enum import Enum
from typing import Optional, Set
from concurrent.futures import ThreadPoolExecutor

#Third Party Imports    
from aiortc import MediaStreamTrack
from aiortc.contrib.media import MediaRelay

#Local Application Imports
from client import Client
from camera_controller import CameraController

Cameras = {
    'Central': {
        'user': username,
        'password': password,
        'rtsp_url': f'rtsp://{username}:{password}@10.20.64.158:554/rtsp/video2',
        'ip': '10.20.64.158',
        'ptz_port': 80,
        'rtsp_port': 554,
    }
}


class CameraState(Enum):
    OFFLINE = 0
    ONLINE = 1
    UNAVAILABLE = 2


class Camera:
    def __init__(self, camera_id: str, camera_data: dict):
        self.id = camera_id
        self.user = camera_data['user']
        self.password = camera_data['password']
        self.ip = camera_data['ip']
        self.rtsp_port = camera_data['rtsp_port']
        self.ptz_port = camera_data['ptz_port']
        self.rtsp_url = f'rtsp://{self.user}:{self.password}@{self.ip}:{self.rtsp_port}/rtsp/video2'
        self.state = CameraState.OFFLINE
        self.url: str = camera_data['rtsp_url']
        self.player: Optional[MediaStreamTrack] = None
        self.relay: Optional[MediaRelay] = None
        self.connected_clients: Set[Client] = set()
        self.executor: ThreadPoolExecutor = ThreadPoolExecutor(max_workers=5)
        self.controller: Optional[CameraController] = None


x = Camera("Hello", Cameras)