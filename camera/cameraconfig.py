# Standard library imports
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict

@dataclass
class CameraConfig:
    user: str
    password: str
    ip: str
    rtsp_port: int
    ptz_port: int
    rtsp_url: str = field(init=False)

    def __post_init__(self):
        self.rtsp_url = f'rtsp://{self.user}:{self.password}@{self.ip}:{self.rtsp_port}/rtsp/video2'

    @classmethod
    def from_dict(cls, data: Dict[str, str]) -> 'CameraConfig':
        return cls(
            user=data['user'],
            password=data['password'],
            ip=data['ip'],
            rtsp_port=int(data['rtsp_port']),
            ptz_port=int(data['ptz_port'])
        )

class CameraState(Enum):
    OFFLINE = 0
    ONLINE = 1
    UNAVAILABLE = 2
