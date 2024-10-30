export default class DynamicHTML {
    createCameraButton(name) {
        const buttonContainer = document.createElement('div');
        buttonContainer.className = 'flex flex-col items-start';

        const button = document.createElement('button');
        button.className = 'flex items-center whitespace-nowrap rounded-md text-sm font-medium hover:bg-muted h-10 px-4 py-2 justify-start gap-2 w-full';
        button.id = `${name}-button`;
        button.onclick = () => window.connectStream(name);

        const icon = document.createElement('i');
        icon.className = 'bi bi-camera';
        button.appendChild(icon);

        const span = document.createElement('span');
        span.id = `${name}-name`;
        span.textContent = name;
        button.appendChild(span);

        buttonContainer.appendChild(button);

        const statusDiv = document.createElement('div');
        statusDiv.id = `${name}-status`;
        statusDiv.className = 'text-xs text-gray-500 mt-1 ml-2';
        statusDiv.textContent = 'Viewer(s): ';
        const viewersSpan = document.createElement('span');
        viewersSpan.id = `${name}-viewers`;
        viewersSpan.textContent = '0';
        statusDiv.appendChild(viewersSpan);
        statusDiv.appendChild(document.createTextNode(' | Status: '));
        const healthSpan = document.createElement('span');
        healthSpan.id = `${name}-health`;
        healthSpan.textContent = 'true';
        statusDiv.appendChild(healthSpan);

        buttonContainer.appendChild(statusDiv);

        return buttonContainer;
    }

    createPresetButton(preset) {
        const buttonContainer = document.createElement('div');
        buttonContainer.className = "flex items-center w-full";

        const button = document.createElement('button');
        button.className = "flex items-center whitespace-nowrap rounded-l-md text-sm font-medium hover:bg-muted h-10 px-4 py-2 flex-grow justify-start gap-2";
        
        const icon = document.createElement('i');
        icon.className = "bi bi-easel text-muted-foreground";
        icon.style.fontSize = "1.5rem";
        button.appendChild(icon);

        const text = document.createTextNode(preset.name);
        button.appendChild(text);

        button.onclick = () => window.ptzGotoPreset(preset.token);

        const deleteButton = document.createElement('button');
        deleteButton.className = "flex items-center justify-center rounded-r-md text-sm font-medium bg-muted-500 text-white hover:bg-red-600 h-10 w-10";
        deleteButton.onclick = (e) => {
            e.stopPropagation();
            window.deletePreset(preset.token);
        };

        const deleteIcon = document.createElement('i');
        deleteIcon.className = "bi bi-x-lg";
        deleteButton.appendChild(deleteIcon);

        buttonContainer.appendChild(button);
        buttonContainer.appendChild(deleteButton);

        return buttonContainer;
    }

    createNewPresetButton() {
        const button = document.createElement('button');
        button.className = "flex items-center whitespace-nowrap rounded-md text-sm font-medium hover:bg-muted text-white h-10 px-4 py-2 w-full justify-center gap-2";
        button.id = "new-preset-button";
        
        const icon = document.createElement('i');
        icon.className = "bi bi-plus-circle";
        icon.style.fontSize = "1.2rem";
        button.appendChild(icon);

        const text = document.createTextNode("New Preset");
        button.appendChild(text);

        button.onclick = () => window.createNewPreset();
        return button;
    }

    createVideoContainer(streamLocal) {
        const containerDiv = document.createElement('div');
        containerDiv.id = `${streamLocal}-container`;
        containerDiv.className = 'relative w-full h-0 pb-[56.25%] opacity-50';

        const video = document.createElement('video');
        video.id = `${streamLocal}-video`;
        video.className = 'absolute top-0 left-0 w-full h-full';
        video.autoplay = true;
        video.playsInline = true;
        video.muted = true;

        // Create unavailable message overlay
        const unavailableOverlay = document.createElement('div');
        unavailableOverlay.id = `${streamLocal}-unavailable`;
        unavailableOverlay.className = 'absolute inset-0 flex items-center justify-center bg-black/50 text-white text-lg font-medium';
        unavailableOverlay.textContent = 'Camera Unavailable';

        video.addEventListener('loadeddata', () => {
            containerDiv.className = 'relative w-full h-0 pb-[56.25%] cursor-pointer';
            containerDiv.onclick = () => {
                const healthElement = document.getElementById(`${streamLocal}-health`);
                if (healthElement && healthElement.textContent !== 'Unavailable') {
                    window.setActiveCamera(streamLocal);
                }
            };
        });

        const activeIndicator = document.createElement('div');
        activeIndicator.id = `${streamLocal}-active`;
        activeIndicator.className = 'absolute top-2 right-2 w-3 h-3 rounded-full bg-green-500 hidden';

        const label = document.createElement('div');
        label.className = 'absolute bottom-2 right-2 bg-black/50 px-2 py-1 rounded text-sm';
        label.textContent = streamLocal;

        const statusDiv = document.createElement('div');
        statusDiv.id = `${streamLocal}-status`;
        statusDiv.className = 'absolute bottom-10 right-2 bg-black/50 px-2 py-1 rounded text-sm';
        statusDiv.textContent = 'Viewer(s): ';
        
        const viewersSpan = document.createElement('span');
        viewersSpan.id = `${streamLocal}-viewers`;
        viewersSpan.textContent = '0';
        statusDiv.appendChild(viewersSpan);
        statusDiv.appendChild(document.createTextNode(' | Status: '));
        
        const healthSpan = document.createElement('span');
        healthSpan.id = `${streamLocal}-health`;
        healthSpan.textContent = 'Unknown';
        statusDiv.appendChild(healthSpan);

        containerDiv.appendChild(video);
        containerDiv.appendChild(unavailableOverlay);
        containerDiv.appendChild(activeIndicator);
        containerDiv.appendChild(label);
        containerDiv.appendChild(statusDiv);
        
        return containerDiv;
    }
}
