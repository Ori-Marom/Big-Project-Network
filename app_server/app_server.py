import socket
import os
import json
import time
from rudp_packet import RUDPHeader
from rudp_core import send_and_wait_for_ack

# Constants for the Application Server
SERVER_IP = "127.0.0.1"
UDP_PORT = 8888
TCP_PORT = 9999
BUFFER_SIZE = 1024
ASSETS_DIR = "assets"
# Maximum packet size for UDP (staying safely under 64KB limit) [cite: 77]
CHUNK_SIZE = 32768


def get_manifest():
    """
    Returns a dictionary of available video qualities (DASH Manifest).
    This allows the client to choose quality based on network conditions[cite: 58].
    """
    return {
        "video_name": "project_video",
        "qualities": ["low", "medium", "high"],
        "files": ["frame1.jpg", "frame2.jpg", "frame3.jpg"]  # Example frames
    }


def send_file_reliable(udp_sock, addr, file_path):
    """
    Reads a file, splits it into chunks, adds RUDP headers,
    and sends each chunk reliably using Stop-and-Wait[cite: 49, 50].
    """
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return

    seq_num = 0
    with open(file_path, 'rb') as f:
        while True:
            data = f.read(CHUNK_SIZE)
            if not data:
                break  # Finished reading file

            # Create RUDP Header with DATA flag [cite: 48]
            header = RUDPHeader(seq_num=seq_num, flags=RUDPHeader.FLAG_DATA)
            packet = header.pack() + data  # Encapsulation

            # Reliability: Send and wait for ACK [cite: 51]
            success = send_and_wait_for_ack(udp_sock, addr, packet, seq_num)

            if not success:
                print(f"Critical error: Failed to send chunk {seq_num}. Aborting.")
                return False

            seq_num += 1

    # Send FIN flag to signal end of stream [cite: 48]
    fin_header = RUDPHeader(seq_num=seq_num, flags=RUDPHeader.FLAG_FIN).pack()
    udp_sock.sendto(fin_header, addr)
    print(f"Successfully finished sending: {file_path}")
    return True


def start_server():
    """Main loop for the Application Server[cite: 42]."""
    print("--- Video Application Server (DASH) Starting ---")

    # UDP socket for RUDP implementation [cite: 48]
    udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_sock.bind((SERVER_IP, UDP_PORT))

    print(f"Server listening on {SERVER_IP}:{UDP_PORT} (UDP/RUDP)")

    while True:
        try:
            # Receive request from client
            data, addr = udp_sock.recvfrom(BUFFER_SIZE)
            message = data.decode('utf-8')
            print(f"Request received: '{message}' from {addr}")

            if message == "GET_MANIFEST":
                # Send DASH manifest as JSON [cite: 58]
                manifest = json.dumps(get_manifest())
                udp_sock.sendto(manifest.encode('utf-8'), addr)

            elif message.startswith("REQUEST_CHUNK"):
                # Format: REQUEST_CHUNK:quality:filename
                parts = message.split(":")
                if len(parts) == 3:
                    _, quality, filename = parts
                    file_path = os.path.join(ASSETS_DIR, quality, filename)

                    print(f"Processing request for {filename} at {quality} quality...")
                    send_file_reliable(udp_sock, addr, file_path)
                else:
                    print("Invalid request format.")

        except Exception as e:
            print(f"Server Error: {e}")


if __name__ == "__main__":
    # Ensure directory structure exists [cite: 4]
    for q in ["low", "medium", "high"]:
        path = os.path.join(ASSETS_DIR, q)
        if not os.path.exists(path):
            os.makedirs(path)
            print(f"Created directory: {path}")

    start_server()