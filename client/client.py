# Standard Library Imports
from typing import Optional
import asyncio
from dataclasses import dataclass

# Third Party Imports
from aiortc import RTCDataChannel
from rtc.peer_connection import CustomRTCPeerConnection


@dataclass
class ClientData:
    peer_connection: CustomRTCPeerConnection
    state: Optional[str] = None
    datachannel: Optional[RTCDataChannel] = None
    connection_complete: asyncio.Event = asyncio.Event()

    def __hash__(self):
        # Use peer_connection (or any other immutable identifier) for hashing
        return hash(self.peer_connection)

    def __eq__(self, other):
        if isinstance(other, ClientData):
            # Compare based on peer_connection (or any relevant fields)
            return self.peer_connection == other.peer_connection
        return False
