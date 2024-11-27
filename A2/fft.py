from matplotlib.colors import LogNorm
import matplotlib.pyplot as plt
import numpy as np
import argparse
import cv2
import os
import time

# global variables
BASE_CASE_LENGTH = 16


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

    if not os.path.exists(args.image):
        raise FileNotFoundError("Error: Image not found")
    if args.image is None:
        raise FileNotFoundError("Error: Image not Found")

    """print arguments"""
    print(f"MODE: {args.mode}")
    print(f"IMAGE: {args.image}")

    return args


# computes naive 1D DFT
def dft(signal):

    N = len(signal)  # length of signal we want to decompose

    # initialize output list for DFT coefficients (frequency domain)
    dft = []

    # loop over all frequency indices k
    for k in range(N):
        X_k = 0  # initialize the k-th DFT coefficient

        # loop over all time indices n
        for n in range(N):
            X_k += signal[n] * np.exp(
                -2j * np.pi * k * n / N
            )  # accumulate sum for n = 0,1,2,...,N-1

        # append computed k-th DFT coefficient
        dft.append(X_k)

    return dft


# computes 1D Cooley-Tukey FFT
def fft(signal):

    N = len(signal)  # length of signal we want to decompose

    """Base case: Naive DFT method"""
    if N <= BASE_CASE_LENGTH:
        return dft(signal)

    """Inductive case: Cooley-Tukey FFT method"""
    # split the sum in the even and odd indices
    X_even = signal[0::2]  # elements at even indices
    X_odd = signal[1::2]  # elements at odd indices

    # recursively call FFT for even and odd sums
    fft_even = fft(X_even)
    fft_odd = fft(X_odd)

    # combine odd and even sums back together
    fft_final = [0] * N
    for k in range((N // 2)):
        exponent = np.exp(-2j * np.pi * k / N)
        fft_final[k] = fft_even[k] + exponent * fft_odd[k]  # first half
        fft_final[k + N // 2] = fft_even[k] - exponent * fft_odd[k]  # second half

    return fft_final


# computes 2D Cooley-Tukey FFT
def twod_fft(signal_image):
    """signal_image = np.array(
        [
            [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16],
            [16, 15, 14, 13, 12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1],
        ]
    )"""

    rows, columns = signal_image.shape

    # create two arrays with 0s for row and columns
    fft_row = np.zeros((rows, columns), dtype=complex)
    fft_final = np.zeros((rows, columns), dtype=complex)

    # fft on rows
    for i in range(rows):
        # go row by row
        fft_row[i, :] = fft(signal_image[i, :])

    # now fft the columns on the fft'ed rows
    for j in range(columns):
        # go column by column
        fft_final[:, j] = fft(fft_row[:, j])

    return fft_final


# computes naive 1D inverse DFT
def inverse_dft(signal):

    N = len(signal)  # length of signal we want to decompose

    # initialize output list for inverse DFT coefficients (time domain)
    inverse_dft = []

    # loop over all time indices n
    for n in range(N):
        x_n = 0  # initialize the n-th inverse DFT coefficient

        # loop over all frequency indices k
        for k in range(N):
            x_n += signal[k] * np.exp(
                2j * np.pi * k * n / N
            )  # accumulate sum for k = 0,1,2,...,N-1

        # append computed n-th inverse DFT coefficient
        inverse_dft.append(x_n / N)

    return inverse_dft


# computes the inverse 1D Cooley-Tukey FFT
def inverse_fft(signal):

    N = len(signal)  # length of signal we want to decompose

    """Base case: Naive DFT method"""
    if N <= BASE_CASE_LENGTH:
        return inverse_dft(signal)

    """Inductive case: Cooley-Tukey FFT method"""
    # split the sum in the even and odd indices
    x_even = signal[0::2]  # elements at even indices
    x_odd = signal[1::2]  # elements at odd indices

    # recursively call inverse_FFT for even and odd sums
    inverse_fft_even = inverse_fft(x_even)
    inverse_fft_odd = inverse_fft(x_odd)

    # combine odd and even sums back together
    inverse_fft_final = [0] * N
    for k in range((N // 2)):
        exponent = np.exp(2j * np.pi * k / N)
        inverse_fft_final[k] = (
            inverse_fft_even[k] + exponent * inverse_fft_odd[k]
        )  # first half
        inverse_fft_final[k + N // 2] = (
            inverse_fft_even[k] - exponent * inverse_fft_odd[k]
        )  # second half

    return inverse_fft_final


# computes the inverse 2D Cooley-Tukey FFT
def twod_inverse_fft(signal_image):

    rows, coloumns = signal_image.shape

    # create two arrays with 0s for row and columns
    inverse_fft_column = np.zeros((rows, coloumns), dtype=complex)
    inverse_fft_final = np.zeros((rows, coloumns), dtype=complex)

    # inverse fft on columns
    for i in range(coloumns):
        # go row by row
        inverse_fft_column[:, i] = inverse_fft(signal_image[:, i])

    # now inverse fft the rows on the inverse ffted columns
    for k in range(rows):
        # go column by column
        inverse_fft_final[k, :] = inverse_fft(inverse_fft_column[k, :])

    return inverse_fft_final


# finds power of 2
def find_power(height, width):
    return int(2 ** np.ceil(np.log2(height))), int(2 ** np.ceil(np.log2(width)))


# pad image such that its pixels are a power of 2
def pad_image(image):

    height, width = image.shape

    # find the next power of 2
    padded_height, padded_width = find_power(height, width)

    # 2D array filled with 0s with the dimensions of the padded image
    padded_image = np.zeros((padded_height, padded_width), dtype=image.dtype)

    # copy original image into padded array, leaving the rest to 0
    padded_image[:height, :width] = image

    return padded_image


# crop image to remove padded image pixels
def crop(original_image, final_image):

    original_height, original_width = original_image.shape
    return final_image[:original_height, :original_width].copy()


# MODE 1: computes 2D Cooley-Tukey FFT given an image file path
def compute_2d_fft(image_path):

    image_original = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)  # get original image

    padded_image = pad_image(image_original)  # pad the image so that it's a power of 2
    fft_final = twod_fft(padded_image)  # compute 2D Cooley-Tukey FFT

    return image_original, fft_final


# MODE 2: denoises an array (an image) given a 2D FFT
def denoise_image(computed_2d_fft):

    rows, columns = computed_2d_fft.shape

    # create coordinate grids
    Y, X = np.ogrid[:rows, :columns]

    # compute distances to the nearest edge
    dist_y = np.minimum(Y, rows - Y)
    dist_x = np.minimum(X, columns - X)
    distance = np.sqrt(dist_y**2 + dist_x**2)

    # create mask to keep low frequencies (near edges)
    mask = distance <= 90

    # apply mask more efficient than looping
    fft_filtered = computed_2d_fft * mask

    # finally, invert to get back the filtered original image
    denoised_image = twod_inverse_fft(fft_filtered)

    # count the num of non-zero coefficients
    non_zero_count = np.count_nonzero(fft_filtered)

    return denoised_image, non_zero_count


# MODE 3: compresses an array (an image) given a 2D FFT
# by keeping high magnitudes
def compress_image_high_magnitudes(computed_2d_fft, compression_level):

    # flatten FFT into 1D to get magnitudes
    magnitude = np.abs(computed_2d_fft)

    # compute magnitude threshold for given compression %
    threshold = np.percentile(magnitude, compression_level)

    # create mask to keep coefficients above threshold
    mask = magnitude >= threshold

    # apply mask to retain largest coefficients (more efficient than looping)
    fft_compressed = computed_2d_fft * mask

    # finally, invert to get back the compressed original image
    compressed_image = twod_inverse_fft(fft_compressed)

    # count the num of non-zero coefficients
    non_zero_count = np.count_nonzero(fft_compressed)

    return compressed_image, non_zero_count


# MODE 3: compresses an array (an image) given a 2D FFT
# by keeping low and high frequencies
def compress_image_low_high_frequencies(computed_2d_fft, compression_level):

    # get rows, cols of FFT
    rows, columns = computed_2d_fft.shape

    """low frequencies"""
    # define low frequency radius (center of FFT), based on compression level
    max_radius = min(rows, columns) // 2  # image size // 2
    radius = int(max_radius * (compression_level / 100))

    # create mask to keep low frequencies
    Y, X = np.ogrid[:rows, :columns]  # create coordinate grids
    dist_y = Y - (rows // 2)  # compute dist_y from center
    dist_x = X - (columns // 2)  # compute dist_x from center
    distance_from_center = np.sqrt(dist_y**2 + dist_x**2)
    mask_low = distance_from_center <= radius  # create mask

    """high frequencies"""
    # flatten FFT into 1D to get higher frequency
    magnitude = np.abs(computed_2d_fft)
    flattened_magnitude = magnitude[~mask_low]  # remove low frequencies

    # calculate compression level for high frequencies after mask_low
    # num of high-f = total - (num of low-f)
    # num of high-f to keep = (total * compression%) - (num of low-f)
    # compression_level_high = (num of high-f to keep) / (num of high-f)
    num_low = np.count_nonzero(mask_low)
    num_high = (rows * columns) - num_low
    num_high_fraction = int((rows * columns * compression_level / 100) - num_low)
    num_high_fraction = max(num_high_fraction, 0)  # edge case
    compression_level_high = num_high_fraction / num_high * 100

    # compute magnitude threshold for given compression %
    threshold = np.percentile(flattened_magnitude, compression_level)

    # create mask to keep high frequencies
    mask_high = (magnitude >= threshold) & ~mask_low

    """low and high frequencies"""
    # combine mask for low and hig frequencies
    mask = mask_low | mask_high

    # apply mask to retain low and high frequencies
    fft_compressed = computed_2d_fft * mask

    # finally, invert to get back the compressed original image
    compressed_image = twod_inverse_fft(fft_compressed)

    # count the num of non-zero coefficients
    non_zero_count = np.count_nonzero(fft_compressed)

    return np.abs(compressed_image), non_zero_count


# MODE 4: analyze runtime complexity


# main
def main():
    """parse command line"""
    # initalize arguments from command line
    args = init_args()

    # MODE 4: Runtime Complexity
    if args.mode == 4:

        # initialize some parameters
        sizes = []
        for i in range(5, 11):
            sizes.append(2**i)  # 2^5 to 2^10

        num_tries = 10  # re-run the experiment at least 10 times
        confidence_mult = 2  # 97% confidence is 2 * std_dev

        # initialize dft and fft stats arrays
        dft_means = []
        dft_variances = []
        dft_std_devs = []
        fft_means = []
        fft_variances = []
        fft_std_devs = []

        # run the experiment for each size
        for size in sizes:

            # initialize dft and fft runtimes arrays
            dft_runtimes = []
            fft_runtimes = []

            # run the experiment 10 times
            for _ in range(num_tries):
                # create random 2D array
                random_array = np.random.rand(size, size)

                # get dft runtime
                start = time.perf_counter()
                dft(random_array)
                end = time.perf_counter()
                dft_runtimes.append(end - start)

                # get fft runtime
                start = time.perf_counter()
                fft(random_array)
                end = time.perf_counter()
                fft_runtimes.append(end - start)

            # compute dft and fft stats
            dft_means.append(np.mean(dft_runtimes))
            dft_variances.append(np.var(dft_runtimes))
            dft_std_devs.append(np.std(dft_runtimes))
            fft_means.append(np.mean(fft_runtimes))
            fft_variances.append(np.var(fft_runtimes))
            fft_std_devs.append(np.std(fft_runtimes))

        # print means and variances to command line
        i = 0
        for size in sizes:
            print(f"---------- Problem Size {size} * {size} Matrix ----------")
            print(f"Naive DFT runtime mean: {dft_means[i]}")
            print(f"Naive DFT runtime variance: {dft_variances[i]}")
            print(f"Cooley-Tukey FFT runtime mean: {fft_means[i]}")
            print(f"Cooley-Tukey FFT runtime variance: {fft_variances[i]}\n")
            i += 1

        # compute error bars proportional to std_dev * confidence_mult
        # for 97% confidence interval
        dft_error_bars = []
        fft_error_bars = []
        for std in dft_std_devs:
            dft_error_bars.append(confidence_mult * std)
        for std in fft_std_devs:
            fft_error_bars.append(confidence_mult * std)

        # display the result
        plt.figure(figsize=(10, 6))

        plt.errorbar(
            sizes,
            dft_means,
            yerr=dft_error_bars,
            label="Naive DFT",
            capsize=5,
            color="mediumpurple",
        )
        plt.errorbar(
            sizes,
            fft_means,
            yerr=fft_error_bars,
            label="Cooley-Tukey FFT",
            capsize=5,
            color="lightcoral",
        )

        plt.xlabel("Problem Size (N x N Matrix)")
        plt.ylabel("Average Runtime Over 10 Runs (in seconds)")
        plt.title("Runtime vs Problem Size for Naive DFT and Cooley-Tukey FFT")
        plt.xscale("log", base=2)
        plt.yscale("log")
        plt.grid(True, which="both", linewidth=0.75)
        plt.legend()
        plt.tight_layout()
        plt.show()

    # MODES 1-3
    else:
        """compute 2D FFT"""
        # compute the 2D FFT of the given image
        original_image, computed_2d_fft_image = compute_2d_fft(args.image)

        """compute program outputs"""
        # MODE 1: Fourier Transform
        if args.mode == 1:

            # crop the image
            final_image = crop(original_image, computed_2d_fft_image)

            # log scale the plot
            ffted_image = np.log(1 + np.abs(final_image))

            # display the result
            plt.figure(figsize=(12, 6))

            plt.subplot(1, 2, 1)  # original image
            plt.imshow(original_image, cmap="gray")
            plt.title("Original Image")
            plt.axis("off")

            plt.subplot(1, 2, 2)  # fourier transform
            plt.imshow(ffted_image, norm=LogNorm(), cmap="gray")
            plt.title("Log-Scaled Fourier Transform")
            plt.axis("off")

            plt.tight_layout()
            plt.show()

        # MODE 2: Denoise
        elif args.mode == 2:

            # denoise the image
            denoised_image, non_zero_count = denoise_image(computed_2d_fft_image)

            # crop the image
            final_image = crop(original_image, denoised_image)

            # transformn complex to float
            final_image = np.abs(final_image)

            # display the result
            plt.figure(figsize=(12, 6))

            plt.subplot(1, 2, 1)  # original image
            plt.imshow(original_image, cmap="gray")
            plt.title("Original Image")
            plt.axis("off")

            plt.subplot(1, 2, 2)  # denoised image
            plt.imshow(final_image, cmap="gray")
            plt.title("Denoised Image")
            plt.axis("off")

            plt.tight_layout()
            plt.show()

            # print num of non-zeros to command line
            print(f"Number of non-zeros for denoised image: {non_zero_count}")

        # MODE 3: Compression
        elif args.mode == 3:

            compression_levels = [0, 50, 75, 90, 97, 99]
            compressed_images = []
            non_zero_counts = []

            # loop trhough compression %'s and compress image
            for level in compression_levels:
                # compress the image
                compressed_image, non_zero_count = compress_image_high_magnitudes(
                    computed_2d_fft_image, level
                )

                # crop the image
                final_image = crop(original_image, compressed_image)

                # transform complex to float
                final_image = np.abs(final_image)

                # append to image list and count list
                compressed_images.append(final_image)
                non_zero_counts.append(non_zero_count)

            # display the results
            plt.figure(figsize=(12, 8))
            for i, (image, level, count) in enumerate(
                zip(compressed_images, compression_levels, non_zero_counts)
            ):
                plt.subplot(2, 3, i + 1)
                plt.imshow(image, cmap="gray")
                plt.title(f"{level}% Compressed Image")
                plt.axis("off")

                # print num of non-zeros to command line
                print(f"Number of non-zeros at {level}% compression: {count}")

            plt.tight_layout()
            plt.show()


if __name__ == "__main__":
    main()
