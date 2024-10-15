# Standard Library Imports
from datetime import timedelta
from typing import Dict
import json

# Third Party Imports
from onvif import ONVIFCamera

# Local Application Imports
from camera.camera_config import CameraConfig
from client.client import ClientData

class CameraController:
    def __init__(self, config: CameraConfig) -> None:
        self.ptz = ONVIFCamera(config.ip, config.ptz_port, config.user, config.password)
        self.ptz_service = self.ptz.create_ptz_service()
        self.media_service = self.ptz.create_media_service()
        self.profile = self.media_service.GetProfiles()[0]
        self.token = self.profile.token


    def handle_ptz_command(self, command: Dict, client: ClientData) -> None:
        if command['command'] == 'move':
            self.move(command['x'], command['y'], command['zoom'])
        elif command['command'] == 'stop':
            self.stop()
        elif command['command'] == 'goto_preset':
            self.goto_preset(command['preset'])
        elif command['command'] == 'get_presets':
            presets = self.get_presets()
            client.datachannel.send(json.dumps({'type': 'presets', 'data': presets}))

    def move(self, x: float, y: float, zoom: float) -> None:
        request = self.ptz_service.create_type('ContinuousMove')
        request.ProfileToken = self.token
        request.Velocity = {
            'PanTilt': {'x': x, 'y': y},
            'Zoom': {'x': zoom}
        }
        request.Timeout = timedelta(seconds=30)
        self.ptz_service.ContinuousMove(request)

    def stop(self) -> None:
        request = self.ptz_service.create_type('Stop')
        request.ProfileToken = self.token
        self.ptz_service.Stop(request)

    def goto_preset(self, preset: str) -> None:
        request = self.ptz_service.create_type('GotoPreset')
        request.ProfileToken = self.token
        request.PresetToken = preset
        self.ptz_service.GotoPreset(request)

    def get_presets(self) -> list:
        presets = self.ptz_service.GetPresets({'ProfileToken': self.token})
        return [{'token': preset.token, 'name': preset.Name} for preset in presets]
