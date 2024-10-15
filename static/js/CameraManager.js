export default class CameraManager {
    constructor(dynamicHTML) {
        this.dynamicHTML = dynamicHTML;
    }

    displayCameras(cameras) {
        const cameraContainer = document.getElementById('cameraButtons');
        cameraContainer.innerHTML = ''; // Clear existing cameras

        cameras.forEach(camera => {
            const buttonElement = this.dynamicHTML.createCameraButton(camera);
            cameraContainer.appendChild(buttonElement);
        });
    }

    displayPresets(presets) {
        const presetContainer = document.getElementById('preset-container');
        presetContainer.innerHTML = ''; // Clear existing presets

        presets.forEach(preset => {
            const button = this.dynamicHTML.createPresetButton(preset);
            presetContainer.appendChild(button);
        });
    }

    updateCameraStatus(cameraName, viewers, health) {
        const viewersElement = document.getElementById(`${cameraName}-viewers`);
        const healthElement = document.getElementById(`${cameraName}-health`);
        const buttonElement = document.getElementById(`${cameraName}-button`);
        
        if (viewersElement) {
            viewersElement.textContent = viewers;
        }
        
        if (healthElement) {
            healthElement.textContent = health;
        }

        if (health === 'Unavailable') {
            buttonElement.disabled = true;
            buttonElement.classList.add('opacity-50', 'pointer-events-none');
        } else {
            buttonElement.disabled = false;
            buttonElement.classList.remove('opacity-50', 'pointer-events-none');
        }
    }
}
