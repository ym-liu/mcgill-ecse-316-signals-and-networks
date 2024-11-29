# mcgill-ecse-316-signals-and-networks
Assignments for ECSE 316 Signals and Networks course offered in Fall 2024 at McGill University

## Authors ##
Dmytro Martyniuk

YuMeng Liu

## Instructions: How to use the program ##

Requires any version of python 3.0+
1. Open a terminal.
2. Clone the repository: ``` git clone https://github.com/ym-liu/mcgill-ecse-316-signals-and-networks.git ```
3. Go to A2 directory: ``` cd A2 ```
3. For a simple query type:
 ```python fft.py -m [mode] -i [image_path]```
in the terminal

## Argumments ##
- mode (optional) is the mode used.

        – [1] (Default )Fast mode: Convert image to FFT form and display.
        – [2] Denoise: The image is denoised by applying an FFT, truncating
        high frequencies and then displayed
        – [3] Compress: Compress image and plot.
        – [4] Plot runtime graphs for the report.
- image_path (optional) is filename of the image for the DFT (default: given image).


## Python Version Used for Testing/Writing the Program ##

```Python 3.11.1```
