import CameraManager from './MultiCameraManager.js';
import { SignallingManager } from './MultiSignalling.js';
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
        this.activeCamera = null;
    }

    init() {
        this.signallingManager.createConnection();
    }

    async connectStream(name) {
        console.log("Connecting to stream:", name);
        try {
            await this.signallingManager.connectStream(name);
        } catch (error) {
            console.error(`Failed to connect to stream ${name}:`, error);
        }
    }

    createNewPreset() {
        const presetName = prompt("Enter a name for the new preset:");
        if (presetName) {
            this.ptzController.createNewPreset(presetName);
        }
    }

    deletePreset(presetToken) {
        if (confirm("Are you sure you want to delete this preset?")) {
            this.ptzController.deletePreset(presetToken);
        }
    }

    setActiveCamera(cameraName) {
        // Remove indicator from previous active camera
        if (this.activeCamera) {
            const prevIndicator = document.getElementById(`${this.activeCamera}-active`);
            if (prevIndicator) prevIndicator.classList.add('hidden');
        }

        this.activeCamera = cameraName;
        this.ptzController.setActiveCamera(cameraName);
        this.ptzController.getPresets();
        
        // Show indicator on new active camera
        const newIndicator = document.getElementById(`${cameraName}-active`);
        if (newIndicator) newIndicator.classList.remove('hidden');
        
        // Enable PTZ controls
        this.ptzController.enable(true);
        
        console.log(`Active camera set to: ${cameraName}`);
    }
}

const app = new App();
document.addEventListener('DOMContentLoaded', () => app.init());

// Make necessary functions available globally
window.connectStream = async (name) => await app.connectStream(name);
window.ptzMove = (x, y, zoom) => app.ptzController.move(x, y, zoom);
window.ptzStop = () => app.ptzController.stop();
window.ptzGotoPreset = (preset) => app.ptzController.gotoPreset(preset);
window.createNewPreset = () => app.createNewPreset();
window.deletePreset = (presetToken) => app.deletePreset(presetToken);

// Add global function for setting active camera
window.setActiveCamera = (name) => app.setActiveCamera(name);
