import CameraManager from './CameraManager.js';
import { SignallingManager } from './signalling.js';
import PTZController from './PTZController.js';
import DynamicHTML from './DynamicHTML.js';

class App {
    constructor() {
        this.dynamicHTML = new DynamicHTML();
        this.cameraManager = new CameraManager(this.dynamicHTML);
        this.ptzController = new PTZController(null); // We'll set this later
        this.signallingManager = new SignallingManager(
            this.cameraManager,
            this.ptzController,
            this.dynamicHTML
        );
        this.ptzController.connectionManager = this.signallingManager; // Set the connection manager for PTZController
    }

    init() {
        this.signallingManager.createConnection();
    }
}

const app = new App();
document.addEventListener('DOMContentLoaded', () => app.init());

// Make necessary functions available globally
window.connectStream = (name) => app.signallingManager.connectStream(name);
window.ptzMove = (x, y, zoom) => app.ptzController.move(x, y, zoom);
window.ptzStop = () => app.ptzController.stop();
window.ptzGotoPreset = (preset) => app.ptzController.gotoPreset(preset);

