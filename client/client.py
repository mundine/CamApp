# Standard Library Imports
from typing import Optional
import asyncio

# Third Party Imports
from aiortc import RTCDataChannel

# Local Application Imports
from rtc.peer_connection import CustomRTCPeerConnection


class Client:
    def __init__(self, peer_connection: CustomRTCPeerConnection):
        self.peer_connection: CustomRTCPeerConnection = peer_connection
        self.state: str = peer_connection.connectionState 
        self.datachannel: Optional[RTCDataChannel] = None
        self.connection_complete = asyncio.Event()

    
