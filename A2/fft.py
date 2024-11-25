from matplotlib.colors import LogNorm
import matplotlib.pyplot as plt
import numpy as np
import argparse
import cv2
import os


def init_args():
    """parse the command line arguments (stdin)"""
    # create a parser
    parser = argparse.ArgumentParser(allow_abbrev=False)

    # optional arguments
    parser.add_argument(
        "-m", type=int, choices=[1, 2, 3, 4], default=1, dest="mode")
    parser.add_argument(
        "-i", type=str, default="moonlanding.png", dest="image")

    # parse the arguments with the previously defined parser
    args = None
    try:
        args = parser.parse_args()
    except SystemExit as error:
        raise

    if not os.path.exists(args.image):
        raise FileNotFoundError("Error: Image not found")
    if args.image is None:
        raise FileNotFoundError("Error: Image not Found")

    """
    Print arguments
    """
    print(f"MODE: {args.mode}")
    print(f"IMAGE: {args.image}")

    return args

# computes 1 fft
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
        exponent = np.exp(-2j * np.pi * k / N)
        fft_final[k] = fft_even[k] + exponent * fft_odd[k]  # First half
        fft_final[k + N // 2] = fft_even[k] - \
            exponent * fft_odd[k]  # Second half

    return fft_final


def twod_fft(signal_image):

    rows, coloumns = signal_image.shape

    # create two arrays with 0s for row and columns
    row_fft = np.zeros((rows, coloumns), dtype=complex)
    final_fft = np.zeros((rows, coloumns), dtype=complex)

    # fft on rows
    for i in range(rows):
        # go row by row
        row_fft[i, :] = fft(signal_image[i, :])

    # now fft the columns on the ffted rows
    for k in range(coloumns):
        # go column by column
        final_fft[:, k] = fft(row_fft[:, k])

    return final_fft

#inverse 1 d fft
def inverse_fft(signal):

    N = len(signal)
    if N <= 16:  # Base case:
        time_domain = []  # Output list for DFT coefficients
        # Loop over all frequency indices k
        for n in range(N):
            x_n = 0  # Initialize the k-th Fourier coefficient
            # Loop over all time indices n
            for k in range(N):
                x_n += signal[k] * np.exp(
                    2j * np.pi * k * n / N
                )  # Accumulate the contribution from x[n]
            time_domain.append(x_n / N)  # Append the result for frequency k
        return time_domain

    # Split input into even and odd indices
    x_even = signal[0::2]  # Elements at even indices
    x_odd = signal[1::2]  # Elements at odd indices

    # Recursive FFT calls for even and odd parts
    inverse_fft_even = inverse_fft(x_even)
    inverse_fft_odd = inverse_fft(x_odd)

    # Combine step
    inverse_fft_final = [0] * N
    for k in range((N // 2)):
        exponent = np.exp(2j * np.pi * k / N)
        inverse_fft_final[k] = (inverse_fft_even[k] + exponent * inverse_fft_odd[k])  # First half
        inverse_fft_final[k + N // 2] = (inverse_fft_even[k] - \
            exponent * inverse_fft_odd[k] ) # Second half

    return inverse_fft_final

# inverse 2d fft
def twod_inverse_fft(signal_image):

    rows, coloumns = signal_image.shape

    # create two arrays with 0s for row and columns
    column_fft = np.zeros((rows, coloumns), dtype=complex)
    final_fft = np.zeros((rows, coloumns), dtype=complex)

    # inverse fft on columns
    for i in range(coloumns):
        # go row by row
        column_fft[:, i] = inverse_fft(signal_image[:, i])

    # now inverse fft the rows on the inverse ffted columns
    for k in range(rows):
        # go column by column
        final_fft[k, :] = inverse_fft(column_fft[k, :])

    return final_fft

def find_power(height, width):
    return int(2 ** np.ceil(np.log2(height))), int(2 ** np.ceil(np.log2(width)))

def pad_image(image):

    height, width = image.shape

    # Fin the next power of 2
    padded_height, padded_width = find_power(height, width)

    # Array with 0s with the dimensions of the padded image
    padded_image = np.zeros((padded_height, padded_width), dtype=image.dtype)

    # Copy the original image into the padded array
    # leaving the rest to 0
    padded_image[:height, :width] = image

    return padded_image

def compute_2d_fft(image_path):

    image_original = cv2.imread(
        image_path, cv2.IMREAD_GRAYSCALE)  # get original image

    padded_image = pad_image(image_original)  # pad teh iamge
    fft_final = twod_fft(padded_image)  # compute 2d fft

    return image_original, fft_final


def denoise_image(computed_2d_fft):

    rows, columns = computed_2d_fft.shape

    # Create coordinate grids
    Y, X = np.ogrid[:rows, :columns]

    # Compute distances to the nearest edge
    dist_y = np.minimum(Y, rows - Y)
    dist_x = np.minimum(X, columns - X)
    distance = np.sqrt(dist_y**2 + dist_x**2)

    # Create a mask to keep low frequencies (near edges)
    mask = distance <= 90

    # Apply the mask more efficient then looping
    filtered_fft = computed_2d_fft * mask

    return filtered_fft

def crop(original_image, final_image):

    original_height, original_width = original_image.shape
    return final_image[:original_height, :original_width]


def main():

    args = init_args()
    # Computes 2d fft
    original_image, computed_2d_fft_image = compute_2d_fft(args.image)

    ########### RESULT ###############

    if args.mode == 1:

        # crop the iamge
        final_image = crop(original_image, computed_2d_fft_image)
        ffted_image = np.log(1 + np.abs(final_image))

        # Display the result
        plt.figure(figsize=(12, 6))

        plt.subplot(1, 2, 1)
        plt.imshow(original_image, cmap="gray")
        plt.title("Original Image")
        plt.axis("off")

        plt.subplot(1, 2, 2)
        plt.imshow(ffted_image, norm=LogNorm(), cmap="gray")
        plt.title("Log-Scaled Fourier Transform")
        plt.axis("off")

        plt.tight_layout()
        plt.show()
    elif args.mode == 2:
        denoised_iamge = denoise_image(computed_2d_fft_image)

        final_denoised_image = twod_inverse_fft(denoised_iamge)
        final_image = crop(original_image, final_denoised_image)

        # transformn complex to float
        final_image = np.abs(final_image)

        plt.figure(figsize=(12, 6))
        plt.subplot(1, 2, 1)
        plt.imshow(original_image, cmap="gray")
        plt.title("Original Image")
        plt.axis("off")

        plt.subplot(1, 2, 2)
        plt.imshow(final_image, cmap="gray")
        plt.title("Denoised Image")
        plt.axis("off")
        plt.tight_layout()
        plt.show()


if __name__ == "__main__":
    main()
