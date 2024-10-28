# Standard Library Imports
from datetime import timedelta
from typing import Dict

# Third Party Imports
from onvif import ONVIFCamera

# Local Application Imports
from camera.camera_config import CameraConfig

class CameraController:
    """
    Controls the PTZ (Pan-Tilt-Zoom) functionality of a camera.
    Interacts with the ONVIF protocol to send commands to the camera.
    """
    def __init__(self, config: CameraConfig) -> None:
        
        self.ptz = ONVIFCamera(config.ip, config.ptz_port, config.user, config.password)
        self.ptz_service = self.ptz.create_ptz_service()
        self.media_service = self.ptz.create_media_service()
        self.profile = self.media_service.GetProfiles()[0]
        self.token = self.profile.token


    def handle_ptz_command(self, command: Dict) -> Dict:
        """
        Handles incoming PTZ commands and executes the appropriate action.

        :param command: The command dictionary containing the action and parameters.
        :return: A response dictionary with the result of the command.
        """
        if command['command'] == 'move':
            self.move(command['x'], command['y'], command['zoom'])
        elif command['command'] == 'stop':
            self.stop()
        elif command['command'] == 'goto_preset':
            self.goto_preset(command['preset'])
        elif command['command'] == 'get_presets':
            presets = self.get_presets()
            return {'type': 'presets', 'data': presets}
        elif command['command'] == 'create_preset':
            result = self.create_preset(command['name'])
            return {'type': 'preset_created', 'success': result['success'], 'name': command['name'], 'error': result.get('error')}
        elif command['command'] == 'delete_preset':
            result = self.delete_preset(command['preset'])
            return {'type': 'preset_deleted', 'success': result['success'], 'error': result.get('error')}
        return None

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
    
    def create_preset(self, name: str) -> Dict:
        try:
            request = self.ptz_service.create_type('SetPreset')
            request.ProfileToken = self.token
            request.PresetName = name
            response = self.ptz_service.SetPreset(request)
            print(response)
            return {'success': True, 'token': response}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def delete_preset(self, preset_token: str) -> Dict:
        try:
            request = self.ptz_service.create_type('RemovePreset')
            request.ProfileToken = self.token
            request.PresetToken = preset_token
            self.ptz_service.RemovePreset(request)
            return {'success': True}
        except Exception as e:
            return {'success': False, 'error': str(e)}
