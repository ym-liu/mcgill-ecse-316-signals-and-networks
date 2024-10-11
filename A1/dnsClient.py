import argparse
import DnsPacket as packet
import DnsResponse as response


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


def print_dns_response_answer(count, records):
    for i in range(count):
        # TODO: [auth | nonauth]
        if records[i]["rtype"] == 0x0001:
            print(f"IP\t{records[i]["rdata"]}\t{records[i]["ttl"]}\t[auth | nonauth]")
        elif records[i]["rtype"] == 0x0002:
            print(f"NS\t{records[i]["rdata"]}\t{records[i]["ttl"]}\t[auth | nonauth]")
        elif records[i]["rtype"] == 0x0005:
            print(
                f"CNAME\t{records[i]["rdata"]}\t{records[i]["ttl"]}\t[auth | nonauth]"
            )
        elif records[i]["rtype"] == 0x000F:
            print(
                f"MX\t{records[i]["rdata"]}\t{records[i]["rdata_preference"]}\t{records[i]["ttl"]}\t[auth | nonauth]"
            )
        else:
            # TODO: error?
            pass


def print_dns_response(args, dns_response):

    # Summarize query that has been sent
    print(f"DnsClient sending request for {args.name}")
    print(f"Server: {args.server}")
    if args.mx:
        qtype = "MX"
    elif args.ns:
        qtype = "NS"
    else:
        qtype = "A"
    print(f"Request type: {qtype}")

    # TODO: Summarize the performance and content of the response
    print(f"Response received after [time] seconds ([num-retries] retries)")

    # Display records in the Answer section
    if dns_response.header["ancount"] > 0:
        print(f"***Answer Section ({dns_response.header["ancount"]} records)***")
    print_dns_response_answer(dns_response.header["ancount"], dns_response.answers)

    # Display records in the Additional section
    if dns_response.header["arcount"] > 0:
        print(f"***Additional Section ({dns_response.header["arcount"]} records)***")
    print_dns_response_answer(dns_response.header["arcount"], dns_response.additional)

    print(f"AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA")
    print(f"Transaction ID: {dns_response.header["id"]}")
    print(f"Flags: {dns_response.header["flags"]}")
    print(
        f"Questions: {dns_response.header["qdcount"]}, Answer RRs: {dns_response.header["ancount"]}, Authority RRs: {dns_response.header["nscount"]}, Additional RRs: {dns_response.header["arcount"]}"
    )
    print(
        f"Domain: {dns_response.question["domain"]}, Type: {dns_response.question["rtype"]}, Class: {dns_response.question["rclass"]}"
    )
    print(f"ANSWER: {dns_response.answers}")
    print(f"ADDITIONAL: {dns_response.additional}")


if __name__ == "__main__":

    print("---------- Parsing the command line arguments (STDIN) ----------")
    args = init_args()

    print("---------- Building and sending DNS query ----------")
    if args.mx:
        qtype = 0x000F
    elif args.ns:
        qtype = 0x0002
    else:
        qtype = 0x0001

    dns_packet = packet.DnsQuery(args.name, qtype)

    print(f"Sending DNS query for {args.name}")
    print(
        f"Timeout is: {args.timeout}, max retires is {args.retries}, mx is: {args.mx}, ns is: {args.ns}, server: {args.server}, domain: {args.name}, qtype: {qtype}"
    )
    raw_response = dns_packet.send(args.server, args.port, args.timeout, args.retries)

    """TODO: wait for response to be returned from server"""
    # Display raw response
    print("Raw response from DNS server:", raw_response)

    print("---------- Interpreting DNS response ----------")
    dns_response = response.DnsResponse(raw_response)

    print("---------- Outputting result to terminal display (STDOUT) ----------")
    print_dns_response(args, dns_response)

    # retransmit queries that are lost
