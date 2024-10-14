from aiortc import RTCPeerConnection, RTCRtpSender
from utils.logger import get_logger
import asyncio

logger = get_logger(__name__)

async def custom_handle_rtcp_packet(self, packet, error_callback=None, peer_connection=None):
    try:
        await RTCRtpSender._handle_rtcp_packet(self, packet)
    except AttributeError as e:
        logger.error(f"Caught AttributeError in RTCRtpSender: {e}")
        if "'RTCRtpSender' object has no attribute '_RTCRtpSender__encoder'" in str(e):
            logger.warning("RTCRtpSender encoder not initialized.")
            if error_callback:
                await error_callback(peer_connection, str(e))
        else:
            logger.error(f"Unexpected AttributeError: {str(e)}")
            if error_callback:
                await error_callback(peer_connection, str(e))
    except Exception as e:
        logger.error(f"Unexpected error in custom_handle_rtcp_packet: {str(e)}")
        if error_callback:
            await error_callback(peer_connection, str(e))

class CustomRTCPeerConnection(RTCPeerConnection):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.error_callback = None
        self.connection_complete = asyncio.Event()
        self.client_id = None
        
    def addTrack(self, track):
        sender = super().addTrack(track)
        
        # Monkey patch the _handle_rtcp_packet method with the error callback and instance reference
        sender._handle_rtcp_packet = lambda packet: custom_handle_rtcp_packet(sender, packet, self.error_callback, self)
        
        return sender

    def set_error_callback(self, callback):
        self.error_callback = callback
