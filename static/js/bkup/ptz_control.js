import { dataChannel } from './connection.js';


export function ptzMove(x_in, y_in, zoom_in) {
    dataChannel.send(JSON.stringify({type: 'ptz', command: "move", x: x_in, y: y_in, zoom: zoom_in}));
}

export function ptzStop() {
    dataChannel.send(JSON.stringify({type: 'ptz', command: "stop"}));
}

export function ptzGotoPreset(preset_in) {
    dataChannel.send(JSON.stringify({type: 'ptz', command: "goto_preset", preset: preset_in}));
}

export function ptzGetPresets() {
    dataChannel.send(JSON.stringify({type: 'ptz', command: "get_presets"}));
}
