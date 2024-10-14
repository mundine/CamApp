import { createConnection, connectStream } from './connection.js';

import { showPopup, closePopup } from './event_listener.js';
import { ptzMove, ptzStop, ptzGotoPreset, ptzGetPresets } from './ptz_control.js';

document.addEventListener('DOMContentLoaded', function() {
    createConnection();
});

// Make functions available globally
window.connectStream = connectStream;
window.ptzMove = ptzMove;
window.ptzStop = ptzStop;
window.ptzGotoPreset = ptzGotoPreset;
window.ptzGetPresets = ptzGetPresets;
window.showPopup = showPopup;
window.closePopup = closePopup;
