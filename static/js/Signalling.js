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
        this.dataChannel = this.peerConnection.createDataChannel("comms");
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
            .then(response => response.json())
            .then(answer => {
                return this.peerConnection.setRemoteDescription(new RTCSessionDescription(answer));
            })
            .catch(error => console.error('Error:', error));
        this.initializeEventListeners();
    }

    connectStream(url) {
        this.streamLocal = url;
        console.log(this.streamLocal);
        this.peerConnection.close();
        this.createConnection();
    }

    initializeEventListeners() {
        console.log("Initializing event listeners");
        console.log(this.peerConnection.dataChannel)
        this.peerConnection.addEventListener("track", (e) => {
            console.log("Track");
            document.getElementById('video').srcObject = e.streams[0];
        });

        this.peerConnection.onconnectionstatechange = (e) => {
            console.log("Connection state: " + this.peerConnection.connectionState);
            if (this.peerConnection.connectionState === 'failed') {
                console.log("Connection closed. Attempting to reconnect...");
                setTimeout(() => this.createConnection(), 5000);
            }
        };

        this.dataChannel.onopen = (e) => {
            console.log("Data channel is open");
            if (this.streamLocal) {
                console.log("tt")
                this.ptzController.getPresets();
            }
        };

        this.dataChannel.onmessage = (e) => {
            let message;
            console.log("Message from DataChannel: " + e.data);
            message = JSON.parse(e.data);
            
            switch(message.type) {
                case "error":
                    this.dynamicHTML.showPopup(message.message);
                    this.ptzController.enable(false);
                    break;
                case "presets":
                    this.cameraManager.displayPresets(message.data);
                    this.ptzController.enable(true);
                    break;
                case "heartbeat":
                    this.handleHeartbeatMessage(message);
                    break;
                case "camera_info":
                    this.cameraManager.displayCameras(message.data);
                    break;
            }
        };
    }

    handleHeartbeatMessage(message) {
        if (message.type === 'heartbeat') {
            const data = message.data;
            for (const [cameraName, cameraData] of Object.entries(data)) {
                this.cameraManager.updateCameraStatus(cameraName, cameraData.viewers, cameraData.health);
            }
        }
    }
}
