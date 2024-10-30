export default class CameraManager {
    constructor(dynamicHTML) {
        this.dynamicHTML = dynamicHTML;
        this.camerasInitialized = false;
        this.connectionQueue = [];
        this.isConnecting = false;
        this.cameraStatuses = new Map(); // Track camera statuses
    }

    displayCameras(cameras) {
        if (this.camerasInitialized) return;
        
        // Create video container for all cameras
        cameras.forEach(camera => {
            const videoContainer = this.dynamicHTML.createVideoContainer(camera);
            const videoGrid = document.getElementById('video-grid');
            videoGrid.appendChild(videoContainer);
            // Initialize status as unavailable until we get heartbeat
            this.cameraStatuses.set(camera, 'Unavailable');
        });
                
        // Don't populate connection queue here anymore
        // We'll wait for heartbeat to determine available cameras
        this.camerasInitialized = true;
    }

    async processNextConnection() {
        if (this.isConnecting || this.connectionQueue.length === 0) return;
        
        this.isConnecting = true;
        const camera = this.connectionQueue.shift();
        
        try {
            console.log(`Connecting to camera: ${camera}`);
            await connectStream(camera);
            
            // Increased delay between connections to ensure stability
            setTimeout(() => {
                this.isConnecting = false;
                this.processNextConnection();
            }, 1000); // Increased from 500ms to 1000ms
            
        } catch (error) {
            console.error(`Failed to connect to camera ${camera}:`, error);
            this.isConnecting = false;
            // Add to back of queue for retry
            this.connectionQueue.push(camera);
            setTimeout(() => this.processNextConnection(), 2000);
        }
    }

    displayPresets(presets) {
        const presetContainer = document.getElementById('preset-container');
        presetContainer.innerHTML = '';

        presets.forEach(preset => {
            const button = this.dynamicHTML.createPresetButton(preset);
            presetContainer.appendChild(button);
        });

        const newPresetButton = this.dynamicHTML.createNewPresetButton();
        presetContainer.appendChild(newPresetButton);
    }

    updateCameraStatus(cameraName, viewers, status) {
        const viewersElement = document.getElementById(`${cameraName}-viewers`);
        const healthElement = document.getElementById(`${cameraName}-health`);
        const unavailableOverlay = document.getElementById(`${cameraName}-unavailable`);
        const oldStatus = this.cameraStatuses.get(cameraName);
        
        if (viewersElement) {
            viewersElement.textContent = viewers;
        }
        
        if (healthElement) {
            healthElement.textContent = status;
        }

        // Show/hide unavailable message
        if (unavailableOverlay) {
            if (status === 'Unavailable') {
                unavailableOverlay.classList.remove('hidden');
            } else {
                unavailableOverlay.classList.add('hidden');
            }
        }

        // Update status in our tracking
        this.cameraStatuses.set(cameraName, status);

        // If camera becomes available and isn't in queue, add it
        if (status !== 'Unavailable' && oldStatus === 'Unavailable' && 
            !this.connectionQueue.includes(cameraName)) {
            console.log(`Camera ${cameraName} became available, adding to connection queue`);
            this.connectionQueue.push(cameraName);
            this.processNextConnection();
        }
    }
}
