import argparse
import time
import sys
import DnsQuery as query
import DnsResponse as response


class CustomArgumentParser(argparse.ArgumentParser):
    def error(self, error_message):
        print_error(error_message, "syntax")
        sys.exit(2)


def init_args():

    # error handling: ensure correct syntax for args.server (starts with @)
    def ensure_at(value, argument):
        if not value.startswith("@"):
            raise argparse.ArgumentTypeError(f"Argument {argument} must start with @")
        return value

    # error handling: ensure correct syntax for args.timeout and args.retries (positive int)
    def ensure_positive(value, argument):
        try:
            value = int(value)
            if value <= 0:
                raise argparse.ArgumentTypeError(
                    f"Argument {argument} must be strictly positive"
                )
        except ValueError:
            raise argparse.ArgumentTypeError(f"Argument {argument} must be an integer")
        return value

    """parse the command line arguments (stdin)"""
    # create a parser
    parser = CustomArgumentParser(
        allow_abbrev=False  # TODO: allow_abbrev=False doesn't work for some reason
    )

    # optional arguments
    parser.add_argument(
        "-t",
        type=lambda val: ensure_positive(val, "timeout"),
        default=5,
        dest="timeout",
    )
    parser.add_argument(
        "-r",
        type=lambda val: ensure_positive(val, "retries"),
        default=3,
        dest="retries",
    )
    parser.add_argument("-p", type=int, default=53, dest="port")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-mx", action="store_true", default=False)
    group.add_argument("-ns", action="store_true", default=False)

    # required, positional arguments
    parser.add_argument("server", type=lambda val: ensure_at(val, "server"))
    parser.add_argument("name", type=str)

    # parse the arguments with the previously defined parser
    args = None
    try:
        args = parser.parse_args()
    except SystemExit as error:
        raise

    args.server = args.server[1:]  # truncate the @

    return args


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


def print_error(error_message, error_type="other"):
    if error_type == "syntax":
        print(f"ERROR\tIncorrect input syntax: {error_message}")
    elif error_type == "maxretries":
        print(f"ERROR\tMaximum number of retries {error_message} exceeded")
    elif error_type == "unexpected":
        print(f"ERROR\tUnexpected response: {error_message}")
    else:
        print(f"ERROR\t{error_message}")


def main():
    """
    Parse the command line arguments (STDIN)
    """
    args = init_args()

    """
    Build DNS query
    """
    if args.mx:
        qtype = 0x000F
    elif args.ns:
        qtype = 0x0002
    else:
        qtype = 0x0001

    dns_query = query.DnsQuery(args.name, qtype)

    # error handling: scan through dns_query to find errors
    # ensure query QR flag is 0
    if dns_query.header.qr != 0:
        print_error("Unexpected query: Query QR flag is not set to 0")
        return

    """
    Send DNS query
    """
    # summarize dns query that has been sent
    print(f"DnsClient sending request for {args.name}")
    print(f"Server: {args.server}")
    if args.mx:
        qtype = "MX"
    elif args.ns:
        qtype = "NS"
    else:
        qtype = "A"
    print(f"Request type: {qtype}")

    # send dns query
    start_time = time.time()
    raw_response, retries = dns_query.send(
        args.server, args.port, args.timeout, args.retries
    )
    end_time = time.time()

    # ensure raw_response is not None
    if raw_response == None:
        return

    """
    Wait for response to be returned from server
    """
    # summarize the performance and content of the response
    print(
        f"Response received after {(end_time - start_time):.5f} seconds ({args.retries - retries} retries)"
    )

    """
    Interprete DNS response
    """
    dns_response = response.DnsResponse(raw_response)

    """
    Error handling: Scan through dns_response to find errors
    If no errors, output result to terminal display (STDOUT)
    """
    # compare id to match up response to request
    if dns_query.header.id != dns_response.header["id"]:
        print_error(
            "Query transaction ID does not match response transaction ID", "unexpected"
        )
    # ensure response QR flag is 1
    elif dns_response.header["flags"]["qr"] != 1:
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

    # if no error, output result to terminal display (STDOUT)
    else:
        print_dns_response(dns_response)


if __name__ == "__main__":
    main()
