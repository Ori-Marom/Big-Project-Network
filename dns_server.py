import socket


class DNSServer:
    def __init__(self, host='127.0.0.1', port=8053):
        self.host = host
        self.port = port
        self.buffer_size = 1024

        # זהו "ספר הטלפונים" של השרת - מילון הממפה שם דומיין לכתובת IP
        # הכתובת 127.0.0.1 היא הכתובת שבה יעבוד שרת האפליקציה של חבר צוות 3
        self.dns_records = {
            "app.server.local": "127.0.0.1"
        }

    def start(self):
        # הגדרת שקע UDP (הפרוטוקול שעליו עובד DNS)
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        server_socket.bind((self.host, self.port))

        print(f"[*] DNS Server is up and listening on {self.host}:{self.port}...")

        try:
            while True:
                # קבלת בקשה מהלקוח
                data, client_address = server_socket.recvfrom(self.buffer_size)
                domain_name = data.decode('utf-8')

                print(f"\n[+] Received DNS query for: '{domain_name}' from {client_address}")

                # חיפוש הדומיין במילון הרשומות שלנו
                if domain_name in self.dns_records:
                    ip_address = self.dns_records[domain_name]
                    response = f"DNS_RESPONSE:{ip_address}"
                    print(f"[>] Resolved '{domain_name}' to IP: {ip_address}")
                else:
                    response = "DNS_RESPONSE:NOT_FOUND"
                    print(f"[-] Domain '{domain_name}' not found in records.")

                # שליחת התשובה חזרה ללקוח
                server_socket.sendto(response.encode('utf-8'), client_address)

        except KeyboardInterrupt:
            print("\n[*] Shutting down DNS Server.")
        finally:
            server_socket.close()


if __name__ == "__main__":
    dns_server = DNSServer()
    dns_server.start()