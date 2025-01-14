import socket
import struct
import threading
import time
from datetime import datetime
import sys
import itertools
import random
import os
import shutil


# ANSI color codes for output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    OKYELLOW = '\033[93m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    RED = '\033[31m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    PURPLE = '\033[35m'
    DARKBLUE = '\033[34m'
    ORANGE = '\033[33m'


# Constants
offer_magic_cookie = 0xabcddcba
offer_message_type = 0x2
request_message_type = 0x3
payload_message_type = 0x4

funny_statistics = [
    "40% of statistics are made up on the spot.",
    "73% of people believe they are better than average drivers.",
    "87% of statistics are fabricated to make a point.",
    "99% of statistics are only 68% accurate.",
    "80% of people claim to like pineapple on pizza, 20% are lying.",
    "65% of people will not read this statistic.",
    "90% of people think they’re above average at multi-tasking.",
    "43% of people believe 100% of statistics they read on the internet.",
    "25% of people make up their own statistics.",
    "50% of people feel better after reading random facts.",
    "72% of people who like cats also like dogs.",
    "33% of statistics are just there to sound smart.",
    "58% of office workers spend 2 hours a day on the internet pretending to work.",
    "94% of people think they can spot a fake laugh.",
    "78% of people don’t remember the last time they did something productive.",
    "55% of adults think cereal is an acceptable dinner.",
    "92% of people who eat chocolate feel instantly happier.",
    "70% of people believe that being late is acceptable if they’re still fashionable.",
    "99% of statistics about happiness involve chocolate.",
    "100% of people who wear glasses say they look smarter.",
    "80% of people believe they are the best cook in the family.",
    "40% of all statistics are completely unrelated to the topic at hand.",
    "67% of people try to avoid doing the dishes after dinner.",
    "59% of people think they can’t live without coffee, the rest have never tried.",
    "86% of people who use umbrellas never actually open them when it rains.",
    "53% of statistics about weight loss are made up while on a diet.",
    "71% of people would rather not talk about how much sleep they’re missing.",
    "63% of people think exercise is overrated, 37% are lying.",
    "77% of office emails have at least one typo.",
    "48% of people have given up on their New Year's resolutions by February.",
    "85% of people who start a sentence with 'I was thinking...' have no plan at all.",
    "91% of adults can't finish a conversation without checking their phone.",
    "62% of people believe they can sing better in the shower than in public.",
    "88% of people believe they’re more productive at night, but actually sleep instead.",
    "50% of people would rather binge-watch TV than read a book.",
    "65% of people wish they had more vacation days but continue working hard.",
    "35% of people argue they make better decisions when sleep-deprived.",
    "77% of people think they’re good at keeping secrets but end up sharing them.",
    "60% of people say they’ll do the laundry tomorrow… but never do.",
    "85% of people overestimate their ability to read a map.",
    "99% of parents say their kids are the most annoying during bedtime.",
    "48% of adults believe they have superpowers after drinking coffee.",
    "70% of office meetings could have been emails.",
    "44% of people forget the name of someone they just met.",
    "89% of drivers believe they are better at parallel parking than others.",
    "58% of people still can’t figure out how to use their smartphone’s features.",
    "72% of people secretly enjoy singing in their car when no one's around.",
    "46% of people claim to be fluent in a second language, but it’s 'Google Translate.'",
    "53% of adults feel more productive when they avoid adult responsibilities.",
    "61% of people believe cats secretly rule the world.",
    "79% of people think they're above average at predicting the future.",
    "66% of people claim they’ve never Googled themselves (but they have)."
]


class SpeedTestClient:
    def __init__(self):
        self.server_ip = None
        self.server_udp_port = None
        self.server_tcp_port = None
        self.running = True
        self.started = False

    def display_icon_message(self):
        """Displays a rectangle with 'Created By' and 'Packet Ninjas' centered in the terminal."""
        if not self.started:
            width = 30  # Width of the rectangle
            message1 = "Created By"
            message2 = "Packet Ninjas"

            try:
                terminal_width = shutil.get_terminal_size(fallback=(80, 20)).columns
            except Exception:
                terminal_width = 80

            padding = max(0, (terminal_width - width) // 2)
            space = " " * padding

            border_top = f"╔{'═' * (width - 2)}╗"  # Top border
            border_bottom = f"╚{'═' * (width - 2)}╝"  # Bottom border
            border_side = f"║{' ' * (width - 2)}║"  # Empty line with side borders
            message_line1 = f"║{message1.center(width - 2)}║"  # Centered "Created By"
            message_line2 = f"║{message2.center(width - 2)}║"  # Centered "Packet Ninjas"

            # Print the centered rectangle
            print(f"{space}{Colors.HEADER}{border_top}{Colors.ENDC}")
            print(f"{space}{Colors.HEADER}{border_side}{Colors.ENDC}")
            print(f"{space}{Colors.HEADER}{message_line1}{Colors.ENDC}")
            print(f"{space}{Colors.HEADER}{message_line2}{Colors.ENDC}")
            print(f"{space}{Colors.HEADER}{border_side}{Colors.ENDC}")
            print(f"{space}{Colors.HEADER}{border_bottom}{Colors.ENDC}")
            self.started = True

    def listen_for_offers(self):
        """Listens for server offers via UDP."""
        self.display_icon_message()

        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as udp_socket:
            udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
            udp_socket.bind(("", 13117))  # Bind to broadcast port

            print(f"{Colors.OKBLUE}Client started, listening for offer requests...{Colors.ENDC}")

            while self.running:
                try:
                    data, addr = udp_socket.recvfrom(8192)
                    magic_cookie, msg_type, udp_port, tcp_port = struct.unpack('!IBHH', data[:9])

                    if magic_cookie == offer_magic_cookie and msg_type == offer_message_type:
                        self.server_ip = addr[0]
                        self.server_udp_port = udp_port
                        self.server_tcp_port = tcp_port
                        print(f"{Colors.OKGREEN}Received offer from {self.server_ip}{Colors.ENDC}")
                        break

                except Exception as e:
                    print(f"{Colors.FAIL}Error receiving offer: {e}{Colors.ENDC}")

    def run_speed_test(self, file_size, tcp_connections, udp_connections):
        """Runs the speed test with the given parameters."""
        threads = []

        # Start UDP connections
        for i in range(udp_connections):
            thread = threading.Thread(target=self.udp_test, args=(file_size, i + 1))
            threads.append(thread)
            thread.start()
        # Start TCP connections
        for i in range(tcp_connections):
            thread = threading.Thread(target=self.tcp_test, args=(file_size, i + 1))
            threads.append(thread)
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        print(f"{Colors.OKBLUE}All transfers complete, listening to offer requests{Colors.ENDC}")

    def tcp_test(self, file_size, connection_id):
        """Performs a TCP speed test."""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as tcp_socket:
                tcp_socket.connect((self.server_ip, self.server_tcp_port))

                # Send file size request
                tcp_socket.sendall(f"{file_size}\n".encode())

                start_time = datetime.now()
                received_data = 0

                while True:
                    data = tcp_socket.recv(8192)
                    if not data:
                        break
                    received_data += len(data)

                total_time = (datetime.now() - start_time).total_seconds()
                speed = (received_data * 8) / total_time if total_time > 0 else 0
                print(
                    f"{Colors.OKCYAN}\u25CFTCP transfer #{connection_id} finished, total time: {total_time:.4f} seconds, total speed: {speed:.4f} bits/second{Colors.ENDC}")

        except Exception as e:
            print(f"{Colors.FAIL}Error in TCP test #{connection_id}: {e}{Colors.ENDC}")

    def udp_test(self, file_size, connection_id):
        """Performs a UDP speed test."""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as udp_socket:
                # Send the request packet to the server
                udp_socket.sendto(
                    struct.pack('!IBQ', offer_magic_cookie, request_message_type, file_size),
                    (self.server_ip, self.server_udp_port)
                )

                start_time = datetime.now()
                received_data = 0
                packets_received = 0
                total_segments = 0  # Default value in case no data is received

                udp_socket.settimeout(1)  # Timeout after 1 second of no data

                while True:
                    try:
                        data, _ = udp_socket.recvfrom(8192)
                        magic_cookie, msg_type, total_segments, current_segment = struct.unpack('!IBQQ', data[:21])

                        # Validate the packet
                        if magic_cookie != offer_magic_cookie or msg_type != payload_message_type:
                            continue

                        packets_received += 1
                        received_data += len(data[21:])  # Only count the payload size

                    except socket.timeout:
                        # Break the loop if no data is received within the timeout period
                        break

                # Calculate the total transfer time
                total_time = (datetime.now() - start_time).total_seconds()
                speed = (received_data * 8) / total_time if total_time > 0 else 0
                percentage_received = (packets_received / total_segments) * 100 if total_segments > 0 else 0
                packets_lost = total_segments - packets_received

                print(
                    f"{Colors.OKYELLOW}\u25CFUDP transfer #{connection_id} finished, "
                    f"total time: {total_time:.4f} seconds, "
                    f"total speed: {speed:.4f} bits/second, "
                    f"percentage of packets received successfully: {percentage_received:.4f}%{Colors.ENDC}"
                )
                print(f"{Colors.RED}\u2605 Interesting statistics:\u2605{Colors.ENDC}")
                print(f"{Colors.RED}\u2605 Packets lost: {packets_lost}{Colors.ENDC}")

                # statistics: Efficiency
                efficiency = (packets_received / total_segments) * 100 if total_segments > 0 else 0
                print(f"{Colors.RED}\u2605 UDP Efficiency: {efficiency:.2f}%{Colors.ENDC}")

                # random funny statistic
                funny_stat = random.choice(funny_statistics)
                print(f"{Colors.HEADER}\u2665 Funny statistic:  \u2665 \n \u2665 {funny_stat}{Colors.ENDC}")

        except Exception as e:
            print(f"{Colors.FAIL}Error in UDP test #{connection_id}: {e}{Colors.ENDC}")


if __name__ == "__main__":
    client = SpeedTestClient()

    while True:
        client.listen_for_offers()

        try:
            sys.stdout.write(f"\n{Colors.PURPLE}\u2605 Enter file size in bytes: {Colors.ENDC}")
            sys.stdout.flush()
            file_size = int(input())

            if file_size <= 0:
                print(f"{Colors.WARNING}Invalid input. File size must be a positive integer.{Colors.ENDC}")
                continue

            sys.stdout.write(f"{Colors.OKBLUE}\u2665 Enter number of TCP connections: {Colors.ENDC}")
            sys.stdout.flush()
            tcp_connections = int(input())

            sys.stdout.write(f"{Colors.ORANGE}\u25A0 Enter number of UDP connections: {Colors.ENDC}")
            sys.stdout.flush()
            udp_connections = int(input())

            if tcp_connections < 0 or udp_connections < 0:
                print(f"{Colors.WARNING}Invalid input. Number of connections must be non-negative.{Colors.ENDC}")
                continue

            client.run_speed_test(file_size, tcp_connections, udp_connections)
        except ValueError:
            print(f"{Colors.FAIL}Invalid input. Please enter numeric values.{Colors.ENDC}")
