# Standard library imports
import asyncio

# Third-party imports   
from aiohttp import web

# Local application imports
from app.app import App
from server.routes import index, javascript, static_files
from rtc.signaling import create_offer_handler

class Server:
    def __init__(self, app: App):
        self.web_app = web.Application()
        self.app = app

    async def setup(self):
        self.web_app.router.add_get("/", index)
        self.web_app.router.add_get("/{filename}.js", javascript)
        self.web_app.router.add_get('/static/{filename}', static_files)
        self.web_app.router.add_post("/offer", create_offer_handler(self.app))
        
        self.web_app.on_shutdown.append(self.shutdown)
        self.web_app.on_startup.append(self.start_background_tasks)
        self.web_app.on_cleanup.append(self.cleanup_background_tasks)

    async def shutdown(self, app):
        for id, client in self.app.clients.items():
            await client.peer_connection.close()

    async def start_background_tasks(self, app):
        app['process_connections_task'] = asyncio.create_task(self.app.process_connections())

    async def cleanup_background_tasks(self, app):
        app['process_connections_task'].cancel()
        await app['process_connections_task']

    def run(self, host: str, port: int):
        web.run_app(self.web_app, host=host, port=port)
