# ASCII Art Converter

A versatile command-line tool written in Python that converts images to ASCII art and plays video files as ASCII animations directly in your terminal.

## Features

- **Image to ASCII**: Convert various image formats (`.jpg`, `.png`, `.bmp`, `.webp`) to ASCII art.
- **Video to ASCII**: Watch video files entirely in ASCII format within your terminal window.
- **Auto-Detection**: Automatically designates the input source as an image or a video based on its file extension.
- **Export to Text**: Save your generated image ASCII art straightforwardly into a `.txt` file.
- **Real-time Rendering & Image Enhancements**: Powered by OpenCV, the script supports Contrast Enhancement (CLAHE), Gamma Correction, Edge Enhancement (Canny), and Bayer Dithering for fine-tuned ASCII fidelity.

## Prerequisites

Ensure you have Python 3.x installed. The following libraries are required:

- OpenCV (`cv2`)
- NumPy (`numpy`)

You can install the dependencies via pip:

```bash
    uv sync
```

or 

```bash
    pip install opencv-python numpy
```

## Usage

Basic usage requires providing an input file path. If no path is provided, it falls back to a default video configured in `backup.py`.

```bash
python src/app/ascii_art.py <path/to/your/file.mp4>
```

### Command-Line Arguments

* **`input`**: (Optional) The path to the image or video file.
* **`-o`, `--output`**: The output file path. Primarily used in `image` mode to export the ASCII character output directly to a text file.
* **`-m`, `--mode`**: Force the processing mode. Supported options:
  * `auto` (default): Detect behavior automatically based on file extension.
  * `image`: Treat the input as a single image.
  * `video`: Treat the input as a continuous video.
* **`--no-clear`**: Disable the terminal clear sequence (useful if logging output streams).

### Examples

**Playing a video as ASCII art:**
```bash
python src/app/ascii_art.py sample_video.mp4
```

**Converting an image to ASCII and displaying it in the terminal:**
```bash
python src/app/ascii_art.py picture.jpg -m image
```

**Converting an image and saving the ASCII art to a text file:**
```bash
python src/app/ascii_art.py landscape.png -o output_art.txt
```

## Configuration

To fine-tune the ASCII generation settings for video playback, you can edit the `CONFIG` dictionary globally declared at the top of `src/app/ascii_art.py`:
- `char_aspect_ratio`: Adjust the aspect ratio depending on your terminal font proportions (default `2.5`).
- `contrast_clip`: Adjust the contrast limit for the CLAHE algorithm (default `0.02`).
- `gamma`: Adjust the video brightness profile (default `0.5`).
- `edge_enhance`: Enable edge highlighting for shape preservation (default `True`).
- `dithering`: Toggle Bayer Dithering pixel transitions (default `False`).
- `target_fps`: Limit the target playback frames per second.
