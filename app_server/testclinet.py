import socket
import struct
from rudp_packet import RUDPHeader

# Client configuration - must match server settings
SERVER_IP = "127.0.0.1"
UDP_PORT = 8888
BUFFER_SIZE = 40000  # Larger than header + chunk size


def start_test_client():
    """
    A test client to verify the RUDP and DASH implementation of the server.
    """
    client_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # Step 1: Request the Manifest (DASH)
    print("Requesting manifest from server...")
    client_sock.sendto(b"GET_MANIFEST", (SERVER_IP, UDP_PORT))

    data, addr = client_sock.recvfrom(2048)
    print(f"Manifest received: {data.decode('utf-8')}")

    # Step 2: Request a specific frame in a specific quality
    # Format: REQUEST_CHUNK:quality:filename
    quality = "high"
    filename = "frame1.jpg"
    request = f"REQUEST_CHUNK:{quality}:{filename}"

    print(f"Requesting {filename} in {quality} quality...")
    client_sock.sendto(request.encode('utf-8'), (SERVER_IP, UDP_PORT))

    # Step 3: Receive the file in chunks and send ACKs
    received_data = b""

    while True:
        packet, addr = client_sock.recvfrom(BUFFER_SIZE)

        # Unpack the RUDP Header
        header_size = struct.calcsize(RUDPHeader.HEADER_FORMAT)
        header_bytes = packet[:header_size]
        payload = packet[header_size:]

        header = RUDPHeader.unpack(header_bytes)

        # Check for FIN flag (End of file)
        if header.flags & RUDPHeader.FLAG_FIN:
            print("Received FIN flag. File transfer complete.")
            break

        print(f"Received chunk {header.seq_num}. Sending ACK...")
        received_data += payload

        # Send ACK back to server
        ack_header = RUDPHeader(ack_num=header.seq_num, flags=RUDPHeader.FLAG_ACK).pack()
        client_sock.sendto(ack_header, addr)

    # Save the received file to check if it's correct
    with open(f"received_{filename}", "wb") as f:
        f.write(received_data)
    print(f"Saved file as received_{filename}")


if __name__ == "__main__":
    start_test_client()