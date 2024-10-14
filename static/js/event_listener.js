
import { peerConnection, dataChannel, createConnection, streamLocal } from './connection.js';
import { displayPresets, displayCameras } from './dynamic_html.js';
import { ptzGetPresets } from './ptz_control.js';

export function initializeEventListeners() {
    console.log("Initializing event listeners");

    //Listener for Track events
    peerConnection.addEventListener(
        "track",
        (e) => {
            console.log("Track");
            document.getElementById('video').srcObject = e.streams[0]; 
        }
    );


    peerConnection.onconnectionstatechange = (e) => {
    console.log("Connection state: " + peerConnection.connectionState);
    if (peerConnection.connectionState === 'failed') {
        console.log("Connection closed. Attempting to reconnect...");
        setTimeout(() => createConnection(), 5000);
    }
    };

    dataChannel.onopen = (e) => {
        console.log("Data channel is open");
        if  (streamLocal) {
            ptzGetPresets();
        }    
    };
    
    dataChannel.onmessage = (e) => {
    let message;
    console.log("Message from DataChannel: " + e.data);
    message = JSON.parse(e.data);
    if (message.type === "error") {
        showPopup(message.message);
        ptzEnable(false)
    }

    if (message.type === 'presets') {
        displayPresets(message.data);
        ptzEnable(true);
    }

    if (message.type === 'heartbeat') {
        handleHeartbeatMessage(message);
    }

    if (message.type == 'camera_info') {
        let cameras = message.data.map(camera => camera);
        displayCameras(cameras);
    }
    
};
}

export function showPopup(message) {
    const popup = document.getElementById('popup');
    const popupMessage = document.getElementById('popup-message');
    popupMessage.textContent = message;
    popup.classList.remove('hidden');
}

export function closePopup() {
    const popup = document.getElementById('popup');
    popup.classList.add('hidden');
}


function handleHeartbeatMessage(message) {
    if (message.type === 'heartbeat') {
        const data = message.data;
        for (const [cameraName, cameraData] of Object.entries(data)) {
            const viewersElement = document.getElementById(`${cameraName}-viewers`);
            const healthElement = document.getElementById(`${cameraName}-health`);
            const buttonElement = document.getElementById(`${cameraName}-button`)
            
            if (viewersElement) {
                viewersElement.textContent = cameraData.viewers;
            }
            
            if (healthElement) {
                healthElement.textContent = cameraData.health;
            }
            if (cameraData.health === 'Unavailable') {
                buttonElement.disabled = true
                buttonElement.classList.add('opacity-50', 'pointer-events-none');
            }
            else {
                buttonElement.disabled = false
                buttonElement.classList.remove('opacity-50', 'pointer-events-none');
            }
        }
    }
  }


  export function ptzEnable(en) {
    // Enable and Disable PTZ
    const ptzButtons = document.querySelectorAll('.flex.items-center.justify-center.text-sm.font-medium.hover\\:bg-muted.h-10.w-10.-m-px');
    
    ptzButtons.forEach(button => {
        if (en) {
            button.classList.remove('opacity-50', 'pointer-events-none');
        } else {
            button.classList.add('opacity-50', 'pointer-events-none');
        }
    });
}
