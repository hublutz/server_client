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

