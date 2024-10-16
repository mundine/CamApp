
from camera.camera import Camera
from camera.camera_config import CameraState
import json

class CameraManager:
    def __init__(self, app_state):
        self.app_state = app_state
        self.cameras: dict[str, Camera] = {}
        self.camera_state = {}

    async def add_camera(self, camera_id: str, camera: Camera):
        self.cameras[camera_id] = Camera(camera_id, camera) 

    async def update_status_data(self): 
        new_status_data = {}
        for camera_id, camera in self.cameras.items():
            if camera.state != CameraState.ONLINE:
                await camera.check_health()
            new_status_data[camera_id] = {
                'status': self.__get_camera_status(camera),
                'clients': camera.clients
            }    
        if new_status_data != self.camera_state:
            self.camera_state = json.dumps({'type': 'heartbeat', 'data': new_status_data})


    
    def __get_camera_status(self, camera: Camera) -> str:
        return {
            CameraState.OFFLINE: 'Offline',
            CameraState.UNAVAILABLE: 'Unavailable',
            CameraState.ONLINE: 'Online'
        }.get(camera.state, 'Unknown')
    
    def send_camera_names(self):
        return json.dumps({'type': 'camera_names', 'data': list(self.cameras.keys())})
