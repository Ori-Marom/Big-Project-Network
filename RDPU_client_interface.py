import struct

# הגדרות רשת קבועות - באחריות הלקוח להתחבר לכתובת זו
SERVER_IP = "10.0.0.10" 
SERVER_PORT = 8080

# פורמט ה-Header הקשיח של הפרוטוקול (20 בייטים)
# Seq(L), Ack(L), Flags(H), Window(L), Checksum(H), PayloadLen(L)
HEADER_FORMAT = "!LLHLHL"

class IMediaClient:
    """
    ממשק מחייב לצוות הלקוח.
    המימוש של הפונקציות הללו יקבע האם השרת יצליח להעביר את המדיה בצורה אמינה.
    """

    def calculate_checksum(self, data):
        """
        חישוב אימות נתונים (16-bit Internet Checksum).
        
        :param data: כל חבילת ה-UDP שהתקבלה (Header + Payload).
        :return: ערך מספרי. אם התוצאה היא 0, החבילה תקינה.
        
        הסבר: השרת מחשב את ה-CS על כל החבילה. על הלקוח להריץ בדיקה זו 
        לפני כל פעולה אחרת. אם התוצאה אינה 0, יש להתעלם מהחבילה (Drop).
        """
        if len(data) % 2 == 1: data += b'\x00'
        s = 0
        for i in range(0, len(data), 2):
            w = (data[i] << 8) + (data[i+1])
            s = (s + w & 0xffff) + ((s + w) >> 16)
        return ~s & 0xffff

    def on_receive_packet(self, raw_data):
        """
        פונקציית הטיפול המרכזית בחבילות נכנסות מהשרת.
        
        :param raw_data: בייטים גולמיים שהתקבלו מה-Socket.
        
        תהליך מצופה מהלקוח:
        1. אימות Checksum: אם לא 0, זרוק את החבילה.
        2. חילוץ Header: שימוש ב-struct.unpack לפי ה-HEADER_FORMAT.
        3. ניהול רצף (Reliability):
           - אם ה-Sequence Number הוא מה שציפית לו: שמור את ה-Payload ושלח ACK (Seq+1).
           - אם ה-Sequence Number גבוה מדי (חבילה אבדה): שלח ACK על המספר שאתה עדיין מחכה לו.
             (שליחת אותו ACK שלוש פעמים תפעיל בשרת Fast Retransmit). 
        """
        pass

    def send_ack(self, next_expected_seq, current_window_size):
        """
        שליחת אישור קבלה (ACK) לשרת.
        
        :param next_expected_seq: מספר החבילה הבאה שהלקוח מצפה לקבל (Cumulative ACK).
        :param current_window_size: גודל הבופר הפנוי בלקוח (Flow Control). 
        
        ציפיית השרת:
        - השרת לא יזיז את חלון השליחה (Sliding Window) ללא קבלת ACK תקין.
        - ה-ACK חייב להישלח כחבילת RUDP עם דגל ACK (0x02) דלוק.
        """
        pass

    def request_media(self, video_name):
        """
        בקשת תוכן מהספק.
        
        :param video_name: שם הקובץ (למשל "movie1").
        
        ציפיית השרת: הודעת טקסט ב-Payload בפורמט: "GET_VIDEO:<name>"
        """
        pass

    def change_quality(self, quality_mode):
        """
        שינוי איכות השידור (DASH Control). [cite: 63]
        
        :param quality_mode: "720p", "360p" או "AUTO".
        
        ציפיית השרת: הודעת טקסט ב-Payload בפורמט: "SET_QUALITY:<mode>"
        ברגע שהלקוח שולח איכות ספציפית, השרת עובר למצב ידני ומתעלם מהמלצות ה-NCA.
        """
        pass