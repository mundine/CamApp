export default class PTZController {
    constructor(connectionManager) {
        this.connectionManager = connectionManager;
    }

    move(x, y, zoom) {
        this.connectionManager.dataChannel.send(JSON.stringify({type: 'ptz', command: "move", x, y, zoom}));
    }

    stop() {
        this.connectionManager.dataChannel.send(JSON.stringify({type: 'ptz', command: "stop"}));
    }

    gotoPreset(preset) {
        this.connectionManager.dataChannel.send(JSON.stringify({type: 'ptz', command: "goto_preset", preset}));
    }

    getPresets() {
        this.connectionManager.dataChannel.send(JSON.stringify({type: 'ptz', command: "get_presets"}));
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
