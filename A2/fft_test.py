from matplotlib.colors import LogNorm
import matplotlib.pyplot as plt
import numpy as np
import argparse
import cv2

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

    args = init_args()

    print(f"MODE: {args.mode}")
    print(f"IMAGE: {args.image}")  # TODO: error if no image found


    ########### RESULT ###############
    if args.mode == 1:

        image = cv2.imread(args.image, cv2.IMREAD_GRAYSCALE) # putin grayscale

        fft_result = np.fft.fft2(image)  # Compute the 2D FFT

        print("OOOOOOOOOOOOOOOOOOOOOOOO")
        print(fft_result)

        # Step 3: Compute the log-scaled magnitude
        magnitude_spectrum = np.log(1 + np.abs(fft_result))  # Log-scaled magnitude spectrum

        # Step 4: Visualize the original image and its Fourier Transform
        plt.figure(figsize=(12, 6))

        # Original image
        plt.subplot(1, 2, 1)
        plt.imshow(image, cmap="gray")
        plt.title("Original Image")
        plt.axis("off")

        # Log-scaled Fourier Transform
        plt.subplot(1, 2, 2)
        plt.imshow(magnitude_spectrum, norm=LogNorm(), cmap="gray")
        plt.title("Log-Scaled Fourier Transform")
        plt.axis("off")

        plt.tight_layout()
        plt.show()

if __name__ == "__main__":
    main()
