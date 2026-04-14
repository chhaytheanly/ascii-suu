import cv2
import numpy as np
import shutil
import sys
import time
import os
import argparse
from backup import DEFAULT_VIDEO

ASCII_CHARS = "  .:-=+*#%"

# For Image Renderer
def image_to_ascii(image_path: str, output_path: str = None) -> str:
    if not os.path.isfile(image_path):
        print(f' Error: Image file not found: {image_path}')
        return ""
    
    frame = cv2.imread(image_path)
    if frame is None:
        print(f' Error: Could not read image: {image_path}')
        return ""

    term_width, term_height = get_terminal_size()
    h, w = frame.shape[:2]

    ascii_width, ascii_height = calculate_ascii_dimensions(w, h, term_width, term_height)
    
    ascii_art = frame_to_ascii(frame, ascii_width, ascii_height)
    
    if output_path:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(ascii_art)
        print(f' ASCII art saved to: {output_path}')
    
    return ascii_art


# For Video Renderer
# ASCII_CHARS = " :-#"
CONFIG = {'char_aspect_ratio': 2.5, 
          'contrast_clip': 0.02, 
          'gamma': 0.5, 
          'edge_enhance': True, 
          'dithering': False, 
          'target_fps': 24.5, 
          'max_width': None}

def get_terminal_size():
    try:
        size = shutil.get_terminal_size()
        return (size.columns, size.lines)
    except:
        return (100, 50)

def apply_contrast_enhancement(gray: np.ndarray, clip_limit: float=0.02) -> np.ndarray:
    if clip_limit <= 0:
        min_val, max_val = (gray.min(), gray.max())
        if max_val > min_val:
            return ((gray - min_val) / (max_val - min_val) * 255).astype(np.uint8)
        return gray
    clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=(8, 8))
    return clahe.apply(gray)

def apply_gamma_correction(gray: np.ndarray, gamma: float=1.0) -> np.ndarray:
    if gamma == 1.0:
        return gray
    inv_gamma = 1.0 / gamma
    table = np.array([(i / 255.0) ** inv_gamma * 255 for i in range(256)]).astype(np.uint8)
    return cv2.LUT(gray, table)

def apply_bayer_dithering(gray: np.ndarray) -> np.ndarray:
    bayer = np.array([[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]], dtype=np.float32) * (255.0 / 16.0) - 128
    h, w = gray.shape
    tiled = np.tile(bayer, (h // 4 + 1, w // 4 + 1))[:h, :w]
    dithered = gray.astype(np.float32) + tiled
    return np.clip(dithered, 0, 255).astype(np.uint8)

def enhance_edges(gray: np.ndarray, strength: float=0.3) -> np.ndarray:
    blurred = cv2.GaussianBlur(gray, (3, 3), 0)
    edges = cv2.Canny(blurred, 50, 150)
    edges = cv2.dilate(edges, np.ones((2, 2), np.uint8), iterations=1)
    return cv2.addWeighted(gray, 1.0 + strength, edges, strength, 0)

def frame_to_ascii(frame: np.ndarray, width: int, height: int) -> str:
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    resized = cv2.resize(gray, (width, height), interpolation=cv2.INTER_AREA)
    resized = apply_contrast_enhancement(resized, CONFIG['contrast_clip'])
    resized = apply_gamma_correction(resized, CONFIG['gamma'])
    if CONFIG['edge_enhance']:
        resized = enhance_edges(resized)
    if CONFIG['dithering']:
        resized = apply_bayer_dithering(resized)
    indices = (resized.astype(np.float32) / 255.0 * (len(ASCII_CHARS) - 1)).astype(np.uint8)
    char_array = np.fromiter(ASCII_CHARS, dtype='U1')[indices]
    lines = []
    for row in char_array:
        lines.append(''.join(row.tolist()))
    return '\n'.join(lines)

def calculate_ascii_dimensions(video_width: float, video_height: float, term_width: int, term_height: int) -> tuple[int, int]:
    video_aspect = video_width / video_height if video_height > 0 else 16 / 9
    char_aspect = CONFIG['char_aspect_ratio']
    ascii_width = CONFIG['max_width'] or term_width
    ascii_height = int(ascii_width / video_aspect / char_aspect)
    if ascii_height > term_height - 2:
        ascii_height = term_height - 2
        ascii_width = int(ascii_height * video_aspect * char_aspect)
    ascii_width = max(40, min(ascii_width, term_width))
    ascii_height = max(20, min(ascii_height, term_height - 2))
    return (ascii_width, ascii_height)

def play_ascii_video(video_path: str):
    if not os.path.isfile(video_path):
        print(f' Error: Video file not found: {video_path}')
        return
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(' Error: Could not open video stream.')
        return
    source_fps = cap.get(cv2.CAP_PROP_FPS)
    fps = CONFIG['target_fps'] if CONFIG['target_fps'] else source_fps if source_fps > 0 else 24.0
    frame_delay = 1.0 / fps
    video_width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
    video_height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
    term_width, term_height = get_terminal_size()
    ascii_width, ascii_height = calculate_ascii_dimensions(video_width, video_height, term_width, term_height)
    sys.stdout.write('\x1b[?25l')
    sys.stdout.write('\x1b[2J\x1b[H')
    sys.stdout.flush()
    frame_count = 0
    start_time = time.time()
    try:
        time.sleep(1)
        while True:
            frame_start = time.time()
            ret, frame = cap.read()
            if not ret:
                break
            ascii_art = frame_to_ascii(frame, ascii_width, ascii_height)
            sys.stdout.write('\x1b[H' + ascii_art)
            sys.stdout.flush()
            elapsed = time.time() - frame_start
            sleep_time = frame_delay - elapsed
            if sleep_time > 0:
                time.sleep(sleep_time)
            frame_count += 1
            if frame_count % 30 == 0:
                current_fps = frame_count / (time.time() - start_time)
                sys.stdout.flush()
    except KeyboardInterrupt:
        print(f'\n\n Interrupted at frame {frame_count}')
    finally:
        cap.release()
        sys.stdout.write('\x1b[?25h')
        sys.stdout.write('\x1b[2J\x1b[H')
        total_time = time.time() - start_time
        avg_fps = frame_count / total_time if total_time > 0 else 0

if __name__ == '__main__':
    
    parser = argparse.ArgumentParser(description='ASCII Art Converter - Image or Video')
    parser.add_argument('input', nargs='?', help='Input file path (image or video)')
    parser.add_argument('-o', '--output', help='Output file path (for image mode, saves ASCII to .txt)')
    parser.add_argument('-m', '--mode', choices=['auto', 'image', 'video'], default='auto',
                        help='Processing mode (default: auto-detect)')
    parser.add_argument('--no-clear', action='store_true', help='Disable terminal clear/animation')
    args = parser.parse_args()
    target_file = args.input or DEFAULT_VIDEO
    
    # Auto-detect mode if not specified
    mode = args.mode
    if mode == 'auto':
        ext = os.path.splitext(target_file)[1].lower()
        mode = 'image' if ext in ['.jpg', '.jpeg', '.png', '.bmp', '.webp'] else 'video'
    
    print(f' Mode: {mode} | Input: {target_file}')
    
    if mode == 'image':
        result = image_to_ascii(target_file, args.output)
        if result and not args.output:
            sys.stdout.write('\x1b[?25l\x1b[2J\x1b[H')  
            print(result)
            sys.stdout.write('\x1b[?25h')  
    else:
        play_ascii_video(target_file)