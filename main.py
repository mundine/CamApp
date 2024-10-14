# Standard library imports
import signal
import sys
from typing import Dict

# Third-party imports
import asyncio
from asyncio import AbstractEventLoop

# Local application imports
from app.app import App
from server.server import Server
from config import Cameras

# Setup signal handlers
def signal_handler(loop: AbstractEventLoop):
    loop.stop()

async def setup_cameras(app: App, cameras: Dict):
    for id, camera_info in cameras.items():
        await app.add_camera(id, camera_info)

def main():
    app = App()
    server = Server(app)
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    loop.run_until_complete(server.setup())
    loop.run_until_complete(setup_cameras(app, Cameras))
    
    if sys.platform == "win32":
        for sig in (signal.SIGINT, signal.SIGTERM):
            signal.signal(sig, lambda s, f: signal_handler(loop))
    
    server.run(host="0.0.0.0", port=5000)

if __name__ == "__main__":
    main()
