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
        const button = document.createElement('button');
        button.className = "flex items-center whitespace-nowrap rounded-md text-sm font-medium hover:bg-muted h-10 px-4 py-2 w-full justify-start gap-2";
        
        const icon = document.createElement('i');
        icon.className = "bi bi-easel text-muted-foreground";
        icon.style.fontSize = "1.5rem";
        button.appendChild(icon);

        const text = document.createTextNode(preset.name);
        button.appendChild(text);

        button.onclick = () => window.ptzGotoPreset(preset.token);
        return button;
    }
}
