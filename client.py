import socket


class Client:
    def __init__(self):
        self.dhcp_server_address = ('127.0.0.1', 67)
        self.dns_server_address = ('127.0.0.1', 8053)  # הוספנו את כתובת ה-DNS
        self.buffer_size = 1024
        self.my_ip = None
        self.app_server_ip = None  # כאן נשמור את הכתובת של שרת האפליקציה שנקבל מה-DNS

    def request_ip(self):
        """פנייה ל-DHCP לקבלת כתובת IP"""
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        client_socket.settimeout(5.0)
        try:
            print(f"[*] Sending to DHCP Server: 'DHCP_DISCOVER'")
            client_socket.sendto("DHCP_DISCOVER".encode('utf-8'), self.dhcp_server_address)

            data, _ = client_socket.recvfrom(self.buffer_size)
            response = data.decode('utf-8')
            print(f"[+] Received response from DHCP: {response}")

            if response.startswith("DHCP_OFFER:"):
                self.my_ip = response.split(":")[1]
                print(f"[V] Success! My new IP address is: {self.my_ip}\n")
                return True
        except socket.timeout:
            print("[-] DHCP Request timed out.")
        finally:
            client_socket.close()
        return False

    def request_dns(self, domain_name):
        """פנייה לשרת ה-DNS כדי למצוא את כתובת ה-IP של שרת היעד"""
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        client_socket.settimeout(5.0)
        try:
            print(f"[*] Asking DNS Server for IP of: '{domain_name}'")
            client_socket.sendto(domain_name.encode('utf-8'), self.dns_server_address)

            data, _ = client_socket.recvfrom(self.buffer_size)
            response = data.decode('utf-8')
            print(f"[+] Received response from DNS: {response}")

            if response.startswith("DNS_RESPONSE:") and "NOT_FOUND" not in response:
                self.app_server_ip = response.split(":")[1]
                print(f"[V] Success! Application Server IP is: {self.app_server_ip}\n")
            else:
                print(f"[-] Could not resolve domain: {domain_name}")

        except socket.timeout:
            print("[-] DNS Request timed out.")
        finally:
            client_socket.close()


if __name__ == "__main__":
    my_client = Client()

    # שלב 1: הלקוח מבקש כתובת IP לעצמו
    if my_client.request_ip():
        # שלב 2: אם הלקוח קיבל כתובת בהצלחה, הוא מחפש את שרת האפליקציה
        my_client.request_dns("app.server.local")
