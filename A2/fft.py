import argparse
import numpy


def init_args():
    """parse the command line arguments (stdin)"""
    # create a parser
    parser = argparse.ArgumentParser(allow_abbrev=False)

    # optional arguments
    parser.add_argument("-m", type=int, choices=[1, 2, 3, 4], default=1, dest="mode")
    parser.add_argument("-i", type=str, default="moonlanding.png", dest="image")

    # parse the arguments with the previously defined parser
    args = None
    try:
        args = parser.parse_args()
    except SystemExit as error:
        raise

    return args


def main():
    """
    Parse the command line arguments (STDIN)
    """
    args = init_args()

    """
    Print arguments
    """
    print(f"MODE: {args.mode}")
    print(f"IMAGE: {args.image}")  # TODO: error if no image found


if __name__ == "__main__":
    main()
