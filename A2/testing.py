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

def fft(signal):

    N = len(signal)

    if N <= 16:  # Base case:
        frequency_domain = []  # Output list for DFT coefficients
        # Loop over all frequency indices k
        for k in range(N):
            x_k = 0  # Initialize the k-th Fourier coefficient
            # Loop over all time indices n
            for n in range(N):
                x_k += signal[n] * np.exp(
                    -2j * np.pi * k * n / N
                )  # Accumulate the contribution from x[n]
            frequency_domain.append(x_k)  # Append the result for frequency k
        return frequency_domain

    # Split input into even and odd indices
    x_even = signal[0::2]  # Elements at even indices
    x_odd = signal[1::2]  # Elements at odd indices

    # Recursive FFT calls for even and odd parts
    fft_even = fft(x_even)
    fft_odd = fft(x_odd)

    # Combine step
    fft_final = [0] * N
    for k in range((N // 2)):
        fft_final[k] = (
            fft_even[k] + np.exp(-2j * np.pi * k / N) * fft_odd[k]
        )  # First half
        fft_final[k + N // 2] = (
            fft_even[k] - np.exp(-2j * np.pi * k / N) * fft_odd[k]
        )  # Second half

    return fft_final

def twod_fft(signal):
    rows, cols = signal.shape

    # Step 1: Apply 1D FFT to each row
    row_transformed = np.zeros((rows, cols), dtype=complex)
    for i in range(rows):
        row_transformed[i, :] = fft(signal[i, :])

    # Step 2: Apply 1D FFT to each column
    col_transformed = np.zeros((rows, cols), dtype=complex)
    for j in range(cols):
        col_transformed[:, j] = fft(row_transformed[:, j])

    return col_transformed

args = init_args()

print(f"MODE: {args.mode}")
print(f"IMAGE: {args.image}")


image = cv2.imread(args.image, cv2.IMREAD_GRAYSCALE) # putin grayscale
'''
fft_result = np.fft.fft2(image)  # Compute the 2D FFT
custom_fft2 = twod_fft(image) # custom two 2d fft

# Compute the difference
difference = np.abs(custom_fft2 - fft_result)
print("Max Difference (2D FFT):", difference.max())
'''
def pad_image_to_power_of_2(image):
    """
    Pads a 2D image with zeros to the next power of 2 for both dimensions.
    """
    height, width = image.shape

    # Find the next power of 2 for height and width
    padded_height = 1 << (height - 1).bit_length()
    padded_width = 1 << (width - 1).bit_length()

    # Create a zero-padded array of the required size
    padded_image = np.zeros((padded_height, padded_width), dtype=image.dtype)

    # Copy the original image into the padded array
    padded_image[:height, :width] = image

    return padded_image

paded_image = pad_image_to_power_of_2(image)

print(np.array(image)[473])
print(len(np.array(image)[473]))
print(np.array(image)[473][629])
row = image[0, :]  # Take the first row
custom_fft_row = fft(row)
numpy_fft_row = np.fft.fft(row)

print("Max Difference (Row FFT):", np.abs(np.array(custom_fft_row) - numpy_fft_row).max())

'''
signal = np.random.rand(474)  # Example signal
fft_even = fft(image[0::2])  # Recursive call
fft_odd = fft(image[1::2])  # Recursive call

numpy_fft_even = np.fft.fft(image[0::2])
numpy_fft_odd = np.fft.fft(image[1::2])

print("Max Difference (Even):", np.abs(np.array(fft_even) - numpy_fft_even).max())
print("Max Difference (Odd):", np.abs(np.array(fft_odd) - numpy_fft_odd).max())
'''