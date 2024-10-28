# Standard library imports
import signal
import sys
from typing import Dict

# Third-party imports
import asyncio

# Local application imports
from app_state import AppState
from server.server import Server
from config import Cameras
from utils.logger import get_logger

# Import Logger
logger = get_logger(__name__)

def signal_handler(signum, frame):
    logger.info(f"Received signal {signum}. Shutting down...")
    sys.exit(0)

async def setup_cameras(app: AppState, cameras: Dict):
    for id, camera_info in cameras.items():
        await app.camera_manager.add_camera(id, camera_info)

def main():
    """
    The main entry point of the application.
    Initializes the application state, sets up the server, and starts the event loop.
    """
    app = AppState()
    server = Server(app)
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    loop.run_until_complete(server.setup())
    loop.run_until_complete(setup_cameras(app, Cameras))
    
    # Set up signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        logger.info("Starting server...")
        server.run(host="0.0.0.0", port=5000)
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received. Shutting down...")
    finally:
        logger.info("Cleaning up...")
        loop.run_until_complete(server.shutdown(app))
        loop.close()

if __name__ == "__main__":
    main()
