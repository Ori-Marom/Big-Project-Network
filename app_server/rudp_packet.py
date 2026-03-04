import struct


class RUDPHeader:
    """
    Represents the custom RUDP Header for reliable transmission.
    Format: !IIBHH (Network byte order: 2 Unsigned Ints, 1 Byte, 2 Unsigned Shorts)
    Total size: 13 bytes.
    """
    # Header Format: SeqNum (4), AckNum (4), Flags (1), WindowSize (2), Checksum (2)
    HEADER_FORMAT = "!IIBHH"

    # Flags to avoid "Magic Numbers"
    FLAG_SYN = 0x01
    FLAG_ACK = 0x02
    FLAG_DATA = 0x04
    FLAG_FIN = 0x08

    def __init__(self, seq_num=0, ack_num=0, flags=0, window_size=1024, checksum=0):
        self.seq_num = seq_num
        self.ack_num = ack_num
        self.flags = flags
        self.window_size = window_size
        self.checksum = checksum

    def pack(self):
        """Converts the header object into bytes for network transmission."""
        return struct.pack(
            self.HEADER_FORMAT,
            self.seq_num,
            self.ack_num,
            self.flags,
            self.window_size,
            self.checksum
        )

    @classmethod
    def unpack(cls, header_bytes):
        """Converts received bytes back into a Header object."""
        data = struct.unpack(cls.HEADER_FORMAT, header_bytes)
        return cls(seq_num=data[0], ack_num=data[1], flags=data[2], window_size=data[3], checksum=data[4])