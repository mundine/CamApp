# Standard Library Imports
import asyncio

# Local Application Imports

from aiortc import RTCPeerConnection, RTCRtpSender
from utils.logger import get_logger


logger = get_logger(__name__)

async def custom_handle_rtcp_packet(self, packet, peer_connection=None):
    try:
        await RTCRtpSender._handle_rtcp_packet(self, packet)
    except AttributeError as e:
        logger.error(f"Caught AttributeError in RTCRtpSender: {e}")
        if "'RTCRtpSender' object has no attribute '_RTCRtpSender__encoder'" in str(e):
            logger.warning("RTCRtpSender encoder not initialized.")
        else:
            logger.error(f"Unexpected AttributeError: {str(e)}")
        peer_connection.close()
    except Exception as e:
        logger.error(f"Unexpected error in custom_handle_rtcp_packet: {str(e)}")
        peer_connection.close()

class CustomRTCPeerConnection(RTCPeerConnection):
    """
    Custom RTCPeerConnection that adds error handling and connection completion events.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.connection_complete = asyncio.Event()
        self.client_id = None
        self.camera_id = None
        self.datachannel = None
        
    def addTrack(self, track):
        """
        Adds a media track to the connection and sets up error handling.
        Specifically patched from original RTCPeerConnection to handle stream failures without crashing program
        :param track: The media track to add.
        :return: The RTCRtpSender for the added track.
        """
        sender = super().addTrack(track)
        
        # Monkey patch the _handle_rtcp_packet method
        sender._handle_rtcp_packet = lambda packet: custom_handle_rtcp_packet(sender, packet, self)
        
        return sender