import matplotlib.pyplot as plt
import numpy as np
import fft


# main
def main():
    """parse command line"""
    # initalize arguments from command line
    args = fft.init_args()

    """compute 2D FFT"""
    # compute the 2D FFT of the given image
    original_image, computed_2d_fft_image = fft.compute_2d_fft(args.image)

    """compute program outputs"""
    # MODE 3: Compression
    if args.mode == 3:

        compression_levels = [0, 50, 75, 90, 97, 99]
        compressed_images = []
        non_zero_counts = []

        # loop trhough compression %'s and compress image
        for level in compression_levels:
            """frequencies"""
            # compress the image
            compressed_image, non_zero_count = fft.compress_image_low_high_frequencies(
                computed_2d_fft_image, level
            )

            # crop the image
            final_image = fft.crop(original_image, compressed_image)

            # transform complex to float
            final_image = np.abs(final_image)

            # append to image list and count list
            compressed_images.append(final_image)
            non_zero_counts.append(non_zero_count)

            """magnitudes"""
            # compress the image
            compressed_image, non_zero_count = fft.compress_image_high_magnitudes(
                computed_2d_fft_image, level
            )

            # crop the image
            final_image = fft.crop(original_image, compressed_image)

            # transform complex to float
            final_image = np.abs(final_image)

            # append to image list and count list
            compressed_images.append(final_image)
            non_zero_counts.append(non_zero_count)

        # display the results
        plt.figure(figsize=(8, 24))
        for i, (image, level, count) in enumerate(
            zip(
                compressed_images,
                sorted(compression_levels + compression_levels),
                non_zero_counts,
            )
        ):
            plt.subplot(6, 2, i + 1)
            plt.imshow(image, cmap="gray")
            if i % 2 == 0:
                plt.title(f"{level}% Compressed Image with Frequencies")
            else:
                plt.title(f"{level}% Compressed Image with Magnitudes")
            plt.axis("off")

            # print num of non-zeros to command line
            print(f"Number of non-zeros at {level}% compression: {count}")

        plt.tight_layout()
        plt.show()


if __name__ == "__main__":
    main()
