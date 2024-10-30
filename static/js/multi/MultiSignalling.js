export class SignallingManager {
    constructor(cameraManager, ptzController, dynamicHTML) {
        this.peerConnection = null;
        this.dataChannel = null;
        this.streamLocal = null;
        this.cameraManager = cameraManager;
        this.ptzController = ptzController;
        this.dynamicHTML = dynamicHTML;
    }

    createConnection() {
        this.peerConnection = new RTCPeerConnection();
        // Always create a data channel
        this.dataChannel = this.peerConnection.createDataChannel("comms");
        this.setupDataChannelListeners();

        this.peerConnection.addTransceiver('video', { direction: 'recvonly' });

        this.peerConnection.createOffer()
            .then(offer => this.peerConnection.setLocalDescription(offer))
            .then(() => {
                return fetch('/offer', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        sdp: this.peerConnection.localDescription.sdp,
                        type: this.peerConnection.localDescription.type,
                        stream: this.streamLocal
                    })
                });
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return response.json();
            })
            .then(answer => {
                return this.peerConnection.setRemoteDescription(new RTCSessionDescription(answer));
            })
            .catch(error => {
                console.error('Error in createConnection:', error);
                // Consider implementing a retry mechanism or user notification here
            });
        this.initializeEventListeners();
    }

    setupDataChannelListeners() {
        this.dataChannel.onopen = (e) => {
            console.log("Data channel is open");
            if (this.streamLocal) {
                //console.log("Requesting presets");
                //this.ptzController.getPresets();
            }
        };

        this.dataChannel.onmessage = (e) => {
            let message;
            console.log("Message from DataChannel: " + e.data);
            message = JSON.parse(e.data);
            
            switch(message.type) {
                case "presets":
                    this.cameraManager.displayPresets(message.data);
                    this.ptzController.enable(true);
                    break;
                case "heartbeat":
                    this.handleHeartbeatMessage(message);
                    break;
                case "camera_info":
                    // Only process camera_info if cameras haven't been displayed yet
                    
                    if (!this.cameraManager.camerasInitialized) {
                        this.peerConnection.close()
                        this.cameraManager.displayCameras(message.data);
                    }
                    break;
                case "preset_created":
                    this.handlePresetCreated(message);
                    break;
                case "preset_deleted":
                    this.handlePresetDeleted(message);
                    break;
            }
        };
    }

    connectStream(url) {
        return new Promise((resolve, reject) => {
            // Check if camera is available before attempting connection
            const status = this.cameraManager.cameraStatuses.get(url);
            if (status === 'Unavailable') {
                reject(new Error("Camera is unavailable"));
                return;
            }

            this.streamLocal = url;
            console.log("Connecting to stream:", this.streamLocal);
            
            // Close existing connection if any
            
            this.createConnection();
            
            // Add connection state change handler to resolve/reject the promise
            this.peerConnection.onconnectionstatechange = (e) => {
                console.log("Connection state:", this.peerConnection.connectionState);
                
                switch (this.peerConnection.connectionState) {
                    case "connected":
                        resolve();
                        break;
                    case "failed":
                        reject(new Error("Connection failed"));
                        break;
                    case "disconnected":
                    case "closed":
                        reject(new Error("Connection closed"));
                        break;
                }
            };
        });
    }

    initializeEventListeners() {
        console.log("Initializing event listeners");
        this.peerConnection.addEventListener("track", (e) => {
            console.log("Track received for stream:", this.streamLocal);
            
            console.log(e)
            // Set the stream to the video element
            document.getElementById(`${this.streamLocal}-video`).srcObject = e.streams[0];            
        });

        this.peerConnection.onconnectionstatechange = (e) => {
            console.log("Connection state: " + this.peerConnection.connectionState);
            if (this.peerConnection.connectionState === 'failed') {
                console.log("Connection closed. Attempting to reconnect...");
                setTimeout(() => this.createConnection(), 5000);
            }
        };
    }

    handleHeartbeatMessage(message) {
        if (message.type === 'heartbeat') {
            const data = message.data;
            for (const [cameraName, cameraData] of Object.entries(data)) {
                this.cameraManager.updateCameraStatus(cameraName, cameraData.clients, cameraData.status);
                
                // If this is the first heartbeat and camera is available, add to connection queue
                if (!this.cameraManager.cameraStatuses.has(cameraName) && 
                    cameraData.status !== 'Unavailable' &&
                    !this.cameraManager.connectionQueue.includes(cameraName)) {
                    this.cameraManager.connectionQueue.push(cameraName);
                    this.cameraManager.processNextConnection();
                }
            }
        }
    }

    handlePresetCreated(message) {
        if (message.success) {
            alert(`Preset "${message.name}" created successfully!`);
            // Refresh the presets list
            this.ptzController.getPresets();
        } else {
            alert(`Failed to create preset: ${message.error}`);
        }
    }

    handlePresetDeleted(message) {
        if (message.success) {
            alert(`Preset deleted successfully!`);
            // Refresh the presets list
            this.ptzController.getPresets();
        } else {
            alert(`Failed to delete preset: ${message.error}`);
        }
    }
}
