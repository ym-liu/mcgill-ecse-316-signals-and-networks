import argparse
import socket
import random
import DnsPacket as packet

if __name__ == "__main__":

    """parse the command line arguments (stdin)"""
    # create a parser
    parser = argparse.ArgumentParser(
        allow_abbrev=False  # TODO: allow_abbrev=False doesn't work for some reason
    )

    # Create an family=INET type=UDP socket
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # optional arguments
    parser.add_argument("-t", type=int, default=5, dest="timeout")
    parser.add_argument("-r", type=int, default=3, dest="max-retries")
    parser.add_argument("-p", type=int, default=53, dest="port")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-mx", action="store_true", default=False)
    group.add_argument("-ns", action="store_true", default=False)

    # required, positional arguments
    parser.add_argument("server", type=str)
    parser.add_argument("name", type=str)

    # parse the arguments with the previously defined parser
    args = parser.parse_args()

    """
    create a DNS query packet with the header and its fields and
    the question which is the domain name itself
    """
    # TODO: Create a DNS query packet: [INSERT OUTLINE]

    """send query to server for given domain name using UDP socket"""
    # TODO: [INSERT OUTLINE]

    # Have to figure out to which DNS server send the DNS packet

    domain = args.name
    dns_packet = packet.DnsQuery(domain)

    print(f"Sending DNS query for {domain}...")
    response = dns_packet.send(args.server, args.port)

    # Display raw response
    print("Raw response from DNS server:", response)

    """wait for response to be returned from server"""
    # TODO: [INSERT OUTLINE]

    """interpret response and output result to terminal display (stdout)"""
    # TODO: [INSERT OUTLINE]
