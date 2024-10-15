# Standard library imports
import asyncio
import time
from collections import defaultdict

# Third-party imports   
from aiohttp import web

# Local application imports
from app_state import AppState
from server.routes import index, javascript, static_files
from rtc.signaling import create_offer_handler
from utils.logger import get_logger

logger = get_logger(__name__)

class RateLimiter:
    def __init__(self, rate_limit, time_period):
        self.rate_limit = rate_limit
        self.time_period = time_period
        self.request_count = defaultdict(list)

    async def check_rate_limit(self, ip_address):
        current_time = time.time()
        self.request_count[ip_address] = [t for t in self.request_count[ip_address] if current_time - t < self.time_period]
        
        if len(self.request_count[ip_address]) >= self.rate_limit:
            return False
        
        self.request_count[ip_address].append(current_time)
        return True

class Server:
    def __init__(self, app: AppState):
        self.web_app = web.Application()
        self.app = app
        self.process_connections_task = None
        self.rate_limiter = RateLimiter(rate_limit=15, time_period=3)  # 15 requests per 3 seconds
        self.heartbeat_task = None

    async def setup(self):
        self.web_app.router.add_get("/", index)
        self.web_app.router.add_get("/{filename}.js", javascript)
        self.web_app.router.add_get('/static/{filename}', static_files)
        self.web_app.router.add_post("/offer", create_offer_handler(self.app))
        
        self.web_app.on_shutdown.append(self.shutdown)
        self.web_app.on_startup.append(self.start_background_tasks)
        self.web_app.on_cleanup.append(self.cleanup_background_tasks)

        # Add middleware for rate limiting
        self.web_app.middlewares.append(self.rate_limit_middleware)

    @web.middleware
    async def rate_limit_middleware(self, request, handler):
        ip_address = request.remote
        if await self.rate_limiter.check_rate_limit(ip_address):
            return await handler(request)
        else:
            raise web.HTTPTooManyRequests(text="Rate limit exceeded")

    async def shutdown(self):
        logger.info("Shutting down server...")
        await self.cleanup_background_tasks(self.web_app)
        for client in self.app.clients:
            await client.peer_connection.close()
        logger.info("Server shutdown complete.")

    async def start_background_tasks(self, app):
        logger.info("Starting background tasks")
        self.process_connections_task = asyncio.create_task(self.app.connection_manager.process_connections())
        self.heartbeat_task = asyncio.create_task(self.app.start_heartbeat())

    async def cleanup_background_tasks(self, app):
        logger.info("Cleaning up background tasks")
        for task in [self.process_connections_task, self.heartbeat_task]:
            if task:
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass

    def run(self, host: str, port: int):
        logger.info(f"Starting server on {host}:{port}")
        web.run_app(self.web_app, host=host, port=port, handle_signals=False)
