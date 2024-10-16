export default class PTZController {
    constructor(connectionManager) {
        this.connectionManager = connectionManager;
        this.activeCamera = null;
    }

    setActiveCamera(cameraName) {
        this.activeCamera = cameraName;
    }

    move(x, y, zoom) {
        this.connectionManager.dataChannel.send(JSON.stringify({
            type: 'ptz',
            command: "move",
            camera: this.activeCamera,
            x, y, zoom
        }));
    }

    stop() {
        this.connectionManager.dataChannel.send(JSON.stringify({
            type: 'ptz',
            command: "stop",
            camera: this.activeCamera
        }));
    }

    gotoPreset(preset) {
        this.connectionManager.dataChannel.send(JSON.stringify({
            type: 'ptz',
            command: "goto_preset",
            camera: this.activeCamera,
            preset
        }));
    }

    getPresets() {
        this.connectionManager.dataChannel.send(JSON.stringify({
            type: 'ptz',
            command: "get_presets",
            camera: this.activeCamera
        }));
    }

    createNewPreset(presetName) {
        this.connectionManager.dataChannel.send(JSON.stringify({
            type: 'ptz',
            command: "create_preset",
            camera: this.activeCamera,
            name: presetName
        }));
    }

    deletePreset(presetToken) {
        this.connectionManager.dataChannel.send(JSON.stringify({
            type: 'ptz',
            command: "delete_preset",
            camera: this.activeCamera,
            preset: presetToken
        }));
    }

    enable(en) {
        const ptzButtons = document.querySelectorAll('.flex.items-center.justify-center.text-sm.font-medium.hover\\:bg-muted.h-10.w-10.-m-px');
        
        ptzButtons.forEach(button => {
            if (en) {
                button.classList.remove('opacity-50', 'pointer-events-none');
            } else {
                button.classList.add('opacity-50', 'pointer-events-none');
            }
        });
    }

    

}
