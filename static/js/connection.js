export let peerConnection;
export let dataChannel;
export let streamLocal;
import { initializeEventListeners } from './event_listener.js';

let clientId = sessionStorage.getItem('client_id') || generateUniqueId();
sessionStorage.setItem('client_id', clientId);


//Create Initial Connection
export function createConnection() {

    peerConnection = new RTCPeerConnection();
    dataChannel = peerConnection.createDataChannel("comms"); 
    peerConnection.addTransceiver('video', { direction: 'recvonly' });
    // Create an offer
    
    peerConnection.createOffer()
        .then(offer => peerConnection.setLocalDescription(offer))
        .then(() => {
            // Send the offer to the server
            return fetch('/offer', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    sdp: peerConnection.localDescription.sdp,
                    type: peerConnection.localDescription.type,
                    client: clientId,
                    stream: streamLocal
                })
            });
        })
        .then(response => response.json())
        .then(answer => {
            // Set the remote description with the answer from the server
            return peerConnection.setRemoteDescription(new RTCSessionDescription(answer));
        })
        .catch(error => console.error('Error:', error));

    initializeEventListeners()
}

//Reconnect logic
export function connectStream(url) {
    streamLocal = url
    peerConnection.close();
    createConnection();
}

//Unique ID for clientID
function generateUniqueId() {
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
        var r = Math.random() * 16 | 0, v = c == 'x' ? r : (r & 0x3 | 0x8);
        return v.toString(16);
    });
}
