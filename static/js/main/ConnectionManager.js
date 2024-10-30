export default class ConnectionManager {
    constructor() {
        this.peerConnection = null;
        this.dataChannel = null;
        this.streamLocal = null;
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
            
            
    }

    connectStream(url) {
        this.streamLocal = url;
        console.log(this.streamLocal);
        this.peerConnection.close();
        this.createConnection();
    }
}
