import CameraManager from './CameraManager.js';
import { SignallingManager } from './Signalling.js';
import PTZController from './PTZController.js';
import DynamicHTML from './DynamicHTML.js';

class App {
    constructor() {
        this.dynamicHTML = new DynamicHTML();
        this.cameraManager = new CameraManager(this.dynamicHTML);
        this.ptzController = new PTZController(null); 
        this.signallingManager = new SignallingManager(
            this.cameraManager,
            this.ptzController,
            this.dynamicHTML
        );
        this.ptzController.connectionManager = this.signallingManager; // Set the connection manager for PTZController
        this.connectStream = this.connectStream.bind(this);
    }

    init() {
        this.signallingManager.createConnection();
    }

    connectStream(name) {
        console.log("Connecting to stream:", name);
        this.ptzController.setActiveCamera(name);
        this.signallingManager.connectStream(name);
    }
}

const app = new App();
document.addEventListener('DOMContentLoaded', () => app.init());

// Make necessary functions available globally
window.connectStream = (name) => app.connectStream(name);
window.ptzMove = (x, y, zoom) => app.ptzController.move(x, y, zoom);
window.ptzStop = () => app.ptzController.stop();
window.ptzGotoPreset = (preset) => app.ptzController.gotoPreset(preset);
