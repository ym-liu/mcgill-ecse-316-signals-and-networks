from matplotlib.colors import LogNorm
import numpy as np

def fft(signal):


    N = len(signal)
    if N <= 16:  # Base case:
        frequency_domain = []  # Output list for DFT coefficients
        # Loop over all frequency indices k
        for k in range(N):
            x_k = 0  # Initialize the k-th Fourier coefficient
            # Loop over all time indices n
            for n in range(N):
                x_k += signal[n] * np.exp(-2j * np.pi * k * n / N)  # Accumulate the contribution from x[n]
            frequency_domain.append(x_k)  # Append the result for frequency k
        return frequency_domain


    # Split input into even and odd indices
    x_even = signal[0::2]  # Elements at even indices
    x_odd = signal[1::2]   # Elements at odd indices

    # Recursive FFT calls for even and odd parts
    fft_even = fft(x_even)
    fft_odd = fft(x_odd)

    # Combine step
    fft_final = [0] * N
    for k in range((N // 2)):
        fft_final[k] = fft_even[k] + np.exp(-2j * np.pi * k / N) * fft_odd[k]  # First half
        fft_final[k + N // 2] = fft_even[k] - np.exp(-2j * np.pi * k / N) * fft_odd[k]  # Second half

    return fft_final

# Example Input
signal = [1, 2, 3, 4, 5, 6, 7, 8, 1, 2, 3, 4, 5, 6, 7, 8, 1, 2, 3, 4, 5, 6, 7, 8,]  # A simple 8-point signal
fft_final = fft(signal)

# Display the result
print("Manual FFT Result:")
print(fft_final)
