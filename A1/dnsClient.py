import argparse
import DnsPacket as packet


def init_args():
    """parse the command line arguments (stdin)"""
    # create a parser
    parser = argparse.ArgumentParser(
        allow_abbrev=False  # TODO: allow_abbrev=False doesn't work for some reason
    )

    # optional arguments
    parser.add_argument("-t", type=int, default=5, dest="timeout")
    parser.add_argument("-r", type=int, default=3, dest="retries")
    parser.add_argument("-p", type=int, default=53, dest="port")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-mx", action="store_true", default=False)
    group.add_argument("-ns", action="store_true", default=False)

    # required, positional arguments
    parser.add_argument("server", type=str)
    parser.add_argument("name", type=str)

    # parse the arguments with the previously defined parser
    return parser.parse_args()


if __name__ == "__main__":

    print("Getting the arguments")
    args = init_args()

    domain = args.name

    if args.mx:
        qtype = 0x000f
    elif args.ns:
        qtype = 0x0002
    else:
        qtype = 0x0001

    dns_packet = packet.DnsQuery(domain, qtype)

    print(f"Sending DNS query for {domain}")
    print(
        f"Timeout is: {args.timeout}, max retires is {args.retries}, mx is: {args.mx}, ns is: {args.ns}, server: {args.server}, domain: {args.name}, qtype: {qtype}")
    response = dns_packet.send(
        args.server, args.port, args.timeout, args.retries)

    # Display raw response
    print("Raw response from DNS server:", response)

    """wait for response to be returned from server"""
    # TODO: [INSERT OUTLINE]

    """interpret response and output result to terminal display (stdout)"""
    # TODO: [INSERT OUTLINE]
