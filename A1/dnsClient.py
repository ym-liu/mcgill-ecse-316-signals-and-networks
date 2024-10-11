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


def print_dns_response_answer(count, aa, records):

    for i in range(count):

        # check if response received is authoritative
        auth = "nonauth"
        if aa:
            auth = "auth"

        # print answer / additional record according to rtype
        if records[i]["rtype"] == 0x0001:
            print(f"IP\t{records[i]["rdata"]}\t{records[i]["ttl"]}\t{auth}")
        elif records[i]["rtype"] == 0x0002:
            print(f"NS\t{records[i]["rdata"]}\t{records[i]["ttl"]}\t{auth}")
        elif records[i]["rtype"] == 0x0005:
            print(f"CNAME\t{records[i]["rdata"]}\t{records[i]["ttl"]}\t{auth}")
        elif records[i]["rtype"] == 0x000F:
            print(
                f"MX\t{records[i]["rdata"]}\t{records[i]["rdata_preference"]}\t{records[i]["ttl"]}\t{auth}"
            )
        else:
            # TODO: error?
            pass


def print_dns_response(dns_response):

    # Display records in the Answer section
    if dns_response.header["ancount"] > 0:
        print(f"***Answer Section ({dns_response.header["ancount"]} records)***")
    print_dns_response_answer(
        dns_response.header["ancount"],
        dns_response.header["flags"]["aa"],
        dns_response.answers,
    )

    # Display records in the Additional section
    if dns_response.header["arcount"] > 0:
        print(f"***Additional Section ({dns_response.header["arcount"]} records)***")
    print_dns_response_answer(
        dns_response.header["arcount"],
        dns_response.header["flags"]["aa"],
        dns_response.additional,
    )

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


def print_error(error_message, error_type="other"):
    if error_type == "syntax":
        print(f"ERROR\tIncorrect input syntax: {error_message}")
    elif error_type == "maxretries":
        print(f"ERROR\tMaximum number of retries {error_message} exceeded")
    elif error_type == "unexpected":
        print(f"ERROR\tUnexpected response: {error_message}")
    else:
        print(f"ERROR\t{error_message}")


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

    print(
        f"Timeout is: {args.timeout}, max retires is {args.retries}, mx is: {args.mx}, ns is: {args.ns}, server: {args.server}, domain: {args.name}, qtype: {qtype}"
    )

    """error handling: scan through dns_packet to find errors"""
    # ensure query QR flag is 0
    if dns_packet.header.qr != 0:
        print_error("Query QR flag is not set to 0", "unexpected")

    raw_response = dns_packet.send(args.server, args.port, args.timeout, args.retries)

    """TODO: wait for response to be returned from server"""
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

    print("---------- Interpreting DNS response ----------")
    # Display raw response
    print("Raw response from DNS server:", raw_response)
    dns_response = response.DnsResponse(raw_response)

    """error handling: scan through dns_response to find errors"""
    # compare id to match up response to request
    if dns_packet.header.id != dns_response.header["id"]:
        print_error(
            "Query transsaction ID does not match response transaction ID", "unexpected"
        )
    # ensure response QR flag is 1
    if dns_response.header["flags"]["qr"] != 1:
        print_error("Response QR flag is not set to 1", "unexpected")
    # ensure response RA flag is 1
    elif dns_response.header["flags"]["ra"] != 1:
        print_error("Server does not support recursive queries", "unexpected")
    # check response RCODE flag for errors
    elif dns_response.header["flags"]["rcode"] == 1:
        print_error("Format error: The name server was unable to interpret the query")
    elif dns_response.header["flags"]["rcode"] == 2:
        print_error(
            "Server failure: The name server was unable to process this query due to a problem with the name server"
        )
    elif dns_response.header["flags"]["rcode"] == 3:
        print(f"NOTFOUND")
    elif dns_response.header["flags"]["rcode"] == 4:
        print_error(
            "Not implemented: The name server does not support the requested kind of query"
        )
    elif dns_response.header["flags"]["rcode"] == 5:
        print_error(
            "Refused: The name server refuses to perform the requested operation for policy reasons"
        )

    else:  # output result to terminal display (STDOUT)
        print_dns_response(dns_response)

    # retransmit queries that are lost
