
from aiortc import RTCPeerConnection, RTCRtpSender



async def custom_handle_rtcp_packet(self, packet, error_callback=None, peer_connection=None):
    try:
        await RTCRtpSender._handle_rtcp_packet(self, packet)
    except AttributeError as e:
        #logger.error(f"Caught AttributeError in RTCRtpSender: {e}")
        if "'RTCRtpSender' object has no attribute '_RTCRtpSender__encoder'" in str(e):
            #logger.warning("RTCRtpSender encoder not initialized.")
            if error_callback:
                await error_callback(peer_connection, str(e))  # Trigger the callback with the peer connection instance
        else:
            if error_callback:
                await error_callback(peer_connection, str(e))  # Trigger the callback with the peer connection instance

class CustomRTCPeerConnection(RTCPeerConnection):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.error_callback = None

    def addTrack(self, track):
        sender = super().addTrack(track)
        
        # Monkey patch the _handle_rtcp_packet method with the error callback and instance reference
        sender._handle_rtcp_packet = lambda packet: custom_handle_rtcp_packet(sender, packet, self.error_callback, self)
        
        return sender

    def set_error_callback(self, callback):
        self.error_callback = callback