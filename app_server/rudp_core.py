import socket
import time

# Constants to avoid "magic numbers" [cite: 5]
RETRANSMIT_TIMEOUT = 1.0  # Seconds to wait for an ACK
MAX_RETRIES = 5  # Maximum times to resend a single packet


def send_and_wait_for_ack(udp_socket, client_address, packet_bytes, seq_num):
    """
    Sends a packet and waits for a specific ACK from the client.
    If no ACK is received, it retransmits the packet. [cite: 50, 55]
    """
    retries = 0
    while retries < MAX_RETRIES:
        # Send the data packet
        udp_socket.sendto(packet_bytes, client_address)

        # Set a timeout for the socket to wait for a response
        udp_socket.settimeout(RETRANSMIT_TIMEOUT)

        try:
            # Wait for ACK from client
            ack_data, addr = udp_socket.recvfrom(1024)

            # Logic to verify if the ACK matches our seq_num
            # (You will use RUDPHeader.unpack here later)
            print(f"Received ACK for packet {seq_num}")
            return True

        except socket.timeout:
            # No ACK received within the timeout period
            retries += 1
            print(f"Timeout! Resending packet {seq_num} (Attempt {retries}/{MAX_RETRIES})")

    print(f"Failed to send packet {seq_num} after {MAX_RETRIES} attempts.")
    return False