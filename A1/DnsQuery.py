import random
import struct
import socket
import dnsClient as client


class DnsHeader:
    def __init__(self):
        # Generate a random 16-bit transaction ID
        self.id = random.randint(0, 65535)
        self.qr = 0  # Query (0)
        self.opcode = 0  # Standard query (0)
        # Authoritative Answer (0 in queries)
        self.aa = 0
        self.tc = 0  # Truncated (0)
        self.rd = 1  # Recursion desired (1)
        # Recursion available (set by the server)
        self.ra = 0
        self.z = 0  # Reserved, must be 0
        self.rcode = 0  # Response code (0 for no error)
        self.qdcount = 1  # Number of questions (1)
        self.ancount = 0  # Number of answers (0 in queries)
        self.nscount = 0  # Number of authority records (0)
        self.arcount = 0  # Number of additional records (0)

    def build(self):

        flags = (
            (self.qr << 15)  # QR field is 1 bit and is placed at bit 15
            | (self.opcode << 11)  # Opcode is 4 bits and occupies bits 11-14
            | (self.aa << 10)  # AA is 1 bit and is placed at bit 10
            | (self.tc << 9)  # TC is 1 bit and is placed at bit 9
            | (self.rd << 8)  # RD is 1 bit and is placed at bit 8
            |
            # RA is 1 bit and is placed at bit 7 (used in responses)
            (self.ra << 7)
            | (self.z << 4)  # Z is 3 bits and occupies bits 4-6
            |
            # RCODE is 4 bits and occupies bits 0-3 (used in responses)
            self.rcode
        )

        # Pack the header fields into a binary format
        header = struct.pack(
            ">HHHHHH",
            self.id,  # Transaction ID
            # Flags (QR, Opcode, AA, TC, RD, RA, Z, RCODE)
            flags,
            self.qdcount,  # Number of questions
            self.ancount,  # Number of answer records
            self.nscount,  # Number of authority records
            self.arcount,
        )  # Number of additional records

        return header


class DnsQuestion:
    def __init__(self, domain, qtype, qclass=0x0001):
        """
        Initializes a DNS Question with:
        - domain: The domain name being queried
        - qtype: The type of query (default is 0x0001, A-record for IP address).
        """
        self.domain = domain
        self.qtype = qtype
        self.qclass = qclass

    def encode_domain_name(self):
        """
        Encodes the domain name (QNAME) according to the DNS protocol.
        Each label is prefixed with its length, and the domain ends with a null byte (0x00).
        """
        labels = self.domain.split(".")
        encoded_name = b""
        for label in labels:
            encoded_name += struct.pack("B", len(label)) + label.encode("utf-8")
        encoded_name += b"\x00"  # Null byte to signal the end of the domain name
        return encoded_name

    def build(self):
        """
        Builds the complete DNS Question section:
        - QNAME: Encoded domain name
        - QTYPE: 16-bit type of query
        - QCLASS: 16-bit class of query
        """
        qname = self.encode_domain_name()
        qtype_qclass = struct.pack(">HH", self.qtype, self.qclass)
        return qname + qtype_qclass


class DnsQuery:
    def __init__(self, domain, qtype, qclass=0x0001):
        # Create instances of DnsHeader and DnsQuestion
        self.header = DnsHeader()
        self.question = DnsQuestion(domain, qtype, qclass)

    def build(self):
        """
        Build the full DNS packet (Header + Question)
        """
        header_packet = self.header.build()
        question_packet = self.question.build()
        return header_packet + question_packet

    def send(self, dns_server, port, timeout, max_retries):
        """
        Sends the DNS query to the specified DNS server and returns the response.
        """
        # Create a UDP socket
        i = 1
        retries = max_retries
        while retries != 0:
            i += 1
            retries -= 1
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                sock.settimeout(timeout)

                # Build the DNS query packet
                query_packet = self.build()

                # Send the packet to the DNS server
                sock.sendto(query_packet, (dns_server, port))

                # Receive the response from the DNS server
                response, _ = sock.recvfrom(512)  # Buffer size is 512 bytes

                # after receiving packet, close socket
                sock.close()

                return response, retries

            except socket.timeout:
                if retries == 0:
                    client.print_error(max_retries, "maxretries")
                    return None, retries  # If retries are exhausted, return None
