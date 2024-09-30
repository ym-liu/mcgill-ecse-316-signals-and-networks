import argparse
import socket

if __name__ == "__main__":

    """parse the command line arguments (stdin)"""
    # create a parser
    parser = argparse.ArgumentParser(
        allow_abbrev=False  # TODO: allow_abbrev=False doesn't work for some reason
    )

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

    """send query to server for given domain name using UDP socket"""
    # TODO: [INSERT OUTLINE]

    """wait for response to be returned from server"""
    # TODO: [INSERT OUTLINE]

    """interpret response and output result to terminal display (stdout)"""
    # TODO: [INSERT OUTLINE]
