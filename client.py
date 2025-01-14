#client
class SpeedTestServer:
    def __init__(self, udp_port, tcp_port):
        self.udp_port = udp_port
        self.tcp_port = tcp_port
        self.server_ip = "0.0.0.0"

    def start(self):
        print(f"Server started, listening on IP address {self.server_ip}")

        udp_thread = threading.Thread(target=self.broadcast_offers)
        udp_thread.daemon = True
        udp_thread.start()

        tcp_thread = threading.Thread(target=self.handle_tcp_requests)
        tcp_thread.daemon = True
        tcp_thread.start()

        udp_request_thread = threading.Thread(target=self.handle_udp_requests)
        udp_request_thread.daemon = True
        udp_request_thread.start()

        udp_thread.join()
        tcp_thread.join()
        udp_request_thread.join()

 def broadcast_offers(self):
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP) as udp_socket:
            udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            #udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            udp_socket.bind((self.server_ip, self.udp_port))
            while True:
                try:
                    message = struct.pack('!IBHH', MAGIC_COOKIE, MESSAGE_TYPE_OFFER, self.udp_port, self.tcp_port)
                    udp_socket.sendto(message, ('<broadcast>', self.udp_port))
                    print(f"Broadcast offer sent on UDP port {self.udp_port}")
                except Exception as e:
                    print(f"Error broadcasting offer: {e}")
                time.sleep(UDP_BROADCAST_INTERVAL)

    def handle_tcp_requests(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as tcp_socket:
            tcp_socket.bind((self.server_ip, self.tcp_port))
            tcp_socket.listen()
            print(f"Listening for TCP connections on port {self.tcp_port}")
            while True:
                client_socket, client_address = tcp_socket.accept()
                threading.Thread(target=self.handle_tcp_connection, args=(client_socket, client_address)).start()

    def handle_tcp_connection(self, client_socket, client_address):
        with client_socket:
            try:
                print(f"TCP connection established with {client_address}")
                file_size = int(client_socket.recv(BUFFER_SIZE).decode('utf-8').strip())
                print(f"TCP request for file size: {file_size} bytes")
                data = b'0' * file_size
                client_socket.sendall(data)
                print(f"TCP transfer to {client_address} completed")
            except Exception as e:
                print(f"Error handling TCP connection: {e}")


    def handle_udp_requests(self):
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as udp_socket:
            udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 8192)
            udp_socket.bind((self.server_ip, self.udp_port))
            print(f"Listening for UDP requests on port {self.udp_port}")
            while True:
                try:
                    data, client_address = udp_socket.recvfrom(BUFFER_SIZE)
                    if len(data) < 13:
                        continue
                    threading.Thread(target=self.handle_udp_connection, args=(udp_socket, data, client_address)).start()
                except Exception as e:
                    print(f"Error receiving UDP request: {e}")

    def handle_udp_connection(self, udp_socket, data, client_address):
        try:
            magic_cookie, message_type, file_size = struct.unpack('!IBQ', data[:13])
            if magic_cookie != MAGIC_COOKIE or message_type != MESSAGE_TYPE_REQUEST:
                print(f"Invalid UDP request from {client_address}")
                return

            print(f"UDP request received from {client_address} for file size: {file_size} bytes")

            segment_count = (file_size // BUFFER_SIZE) + (1 if file_size % BUFFER_SIZE != 0 else 0)

            payload_prefix = struct.pack('!IBQQ', MAGIC_COOKIE, MESSAGE_TYPE_PAYLOAD, segment_count, 0)
            for segment in range(segment_count):
                payload = payload_prefix[:-8] + struct.pack('!Q', segment)  # Update only the segment number
                payload += b'0' * min(BUFFER_SIZE - len(payload), file_size - segment * BUFFER_SIZE)
                udp_socket.sendto(payload, client_address)

            print(f"UDP transfer to {client_address} completed")
        except Exception as e:
            print(f"Error handling UDP connection: {e}")

if __name__ == "__main__":
    udp_port = 13117
    tcp_port = 65432
    server = SpeedTestServer(udp_port, tcp_port)
    server.start()
