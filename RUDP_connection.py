import socket
import random
import time
from RUDP_core import RUDPHeader, RUDPPacket

class RUDPConnection:
    MSS = 1400  
    TIMEOUT = 2.0  

    def __init__(self, port):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind(('0.0.0.0', port))
        self.sock.settimeout(self.TIMEOUT)

    def send_chunk_reliable(self, data, dest_addr, window_size_bytes, nca_instance):
        """
        שליחה אמינה עם תמיכה ב-Fast Retransmit.
        שים לב: הוספתי פרמטר nca_instance כדי שנוכל לעדכן אותו בזמן אמת.
        """
        
        # 1. פילוח (Segmentation)
        packets = []
        for i in range(0, len(data), self.MSS):
            chunk_part = data[i:i + self.MSS]
            header = RUDPHeader(seq=len(packets), flags=RUDPHeader.DATA, payload_len=len(chunk_part))
            packets.append(RUDPPacket(header, chunk_part))

        total_packets = len(packets)
        window_size = max(1, int(window_size_bytes / self.MSS))
        
        base = 0      
        next_seq = 0  
        
        print(f"   [Worker] Start Sending. Total: {total_packets} pkts")

        while base < total_packets:
            # שליחת החלון הנוכחי
            while next_seq < base + window_size and next_seq < total_packets:
                self._send_packet_simulated(packets[next_seq], dest_addr)
                next_seq += 1

            # המתנה לאישורים
            try:
                raw_data, addr = self.sock.recvfrom(1024)
                ack_pkt = RUDPPacket.from_bytes(raw_data)

                if ack_pkt and (ack_pkt.header.flags & RUDPHeader.ACK):
                    ack_num = ack_pkt.header.ack
                    
                    # --- כאן נכנס השינוי של Fast Retransmit ---
                    # אנחנו שולחים ל-NCA את ה-ACK שקיבלנו (הוא מצפה ל-Next Expected Seq)
                    # הלקוח בדרך כלל שולח את המספר שהוא *מחכה* לו. 
                    # אם הלקוח מחכה ל-5, הוא שולח ACK 5. אם הוא שוב מקבל משהו אחר, הוא שוב שולח ACK 5.
                    
                    # ה-NCA בודק אם זה ACK כפול
                    needs_fast_retx = nca_instance.on_ack_received(ack_num, 65535)
                    
                    if needs_fast_retx:
                        print(f"   [!!!] FAST RETRANSMIT TRIGGERED for Packet {base}")
                        # "עובדים" על הלולאה: מחזירים את המצביע אחורה כאילו היה Timeout
                        # אבל עושים זאת מיד!
                        next_seq = base 
                        continue # חוזרים לתחילת ה-While כדי לשדר מיד
                    
                    # טיפול רגיל ב-ACK (קידום החלון)
                    if ack_num > base:
                        base = ack_num
                        # עדכון החלון הדינמי מה-NCA להמשך הריצה
                        window_size = max(1, int(nca_instance.get_allowed_window() / self.MSS))

            except socket.timeout:
                print(f"   [!] Timeout (Slow). Retransmitting from {base}...")
                nca_instance.on_timeout() # עדכון המוח על הכישלון האיטי
                next_seq = base # איפוס לשידור חוזר
                
        return True

    def _send_packet_simulated(self, packet, addr):
        # סיכוי של 5% לאיבוד חבילה
        if random.random() < 0.05:
            print(f"      [~] DROP: Packet {packet.header.seq}")
            return 
        self.sock.sendto(packet.to_bytes(), addr)