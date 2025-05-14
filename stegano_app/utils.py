# utils.py
from PIL import Image

def estimate_capacity(image_file):
    image = Image.open(image_file)
    width, height = image.size
    mode = image.mode

    mode_to_channels = {
        'RGB': 3,
        'RGBA': 4,
        'L': 1,
        'CMYK': 4
    }

    channels = mode_to_channels.get(mode, 3)

    total_bits = width * height * channels
    total_bytes = total_bits // 8
    total_kb = total_bytes / 1024

    return round(total_bytes), round(total_kb, 2)
