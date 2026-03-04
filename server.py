from RUDP_connection import RUDPConnection
from nca import NCA
from RUDP_core import RUDPHeader

class VideoServer:
    def __init__(self):
        # הגדרת הכתובת הקבועה כפי שסוכם עם ה-DHCP
        self.ip = "10.0.0.10" 
        self.port = 8080
        
        self.conn = RUDPConnection(self.port) 
        self.nca = NCA() 
        self.client_addr = None
        self.state = "LISTEN"
        self.user_forced_quality = None

    def handle_handshake(self):
        """לחיצת ידיים מול הלקוח [cite: 42]"""
        print(f"[*] Video Server online at {self.ip}:{self.port}")
        while self.state != "ESTABLISHED":
            packet, addr = self.conn.receive_data()
            if not packet: continue

            if (packet.header.flags & RUDPHeader.SYN):
                self.client_addr = addr
                self.state = "SYN_RCVD"
                # שליחת SYN-ACK
                self.conn.send_control_packet(RUDPHeader.SYN | RUDPHeader.ACK, addr)
            
            elif (packet.header.flags & RUDPHeader.ACK) and self.state == "SYN_RCVD":
                self.state = "ESTABLISHED"
                print(f"[!] Connection with client {addr} established.")

    def stream_media(self, video_name):
        """הזרמת מדיה ב-Chunks תוך התייעצות עם ה-NCA """
        for i in range(10): # סימולציה של 10 מקטעים
            # הבוס (Server) שואל את המוח (NCA)
            recommended = self.nca.recommend_quality()
            window = self.nca.get_allowed_window()
            
            # החלטה סופית: העדפת משתמש מול המלצת רשת
            final_q = self.user_forced_quality if self.user_forced_quality else recommended
            
            print(f"[*] Chunk {i}: Quality={final_q}, Window={window/1400:.1f} pkts")
            
            # הפעלה של ה"עובד" (Connection) לביצוע השליחה הפיזית
            chunk_data = f"DATA_{video_name}_{final_q}_{i}".encode()
            success = self.conn.send_chunk_reliable(chunk_data, self.client_addr, window, self.nca)
            
            # עדכון המוח בתוצאות השטח
            if success:
                self.nca.on_ack_received(i, client_rwnd=65535)
            else:
                self.nca.on_timeout()

    def run(self):
        self.handle_handshake()
        while True:
            packet, addr = self.conn.receive_data()
            if not packet or not packet.payload: continue
            
            msg = packet.payload.decode('utf-8')
            if msg.startswith("SET_QUALITY:"):
                q = msg.split(":")[1]
                self.user_forced_quality = None if q == "AUTO" else q
            elif msg.startswith("GET_VIDEO:"):
                self.stream_media(msg.split(":")[1])

if __name__ == "__main__":
    server = VideoServer()
    server.run()