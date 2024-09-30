import argparse
import socket

if __name__ == "__main__":
    # get the command line arguments (stdin)
    parser = argparse.ArgumentParser()
    parser.add_argument("--timeout", "-t", default=5)
    parser.add_argument("--max_retries", "-r", default=3)
    parser.add_argument("--port", "-p", default=53)
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--mail_server", "-mx", action="store_true", default=False)
    group.add_argument("--name_server", "-ns", action="store_true", default=False)

    args = parser.parse_args()

    # send query to server for given domain name using UDP socket

    # wait for response to be returned from server

    # interpret response and output result to terminal display (stdout)
