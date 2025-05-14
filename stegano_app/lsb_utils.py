import os 
from PIL import Image

# Increase allowed file size (e.g., 2 MB)
MAX_FILE_SIZE = 2 * 1024 * 1024  # 2 MB

def bytes_to_bits(data):
    return ''.join(format(byte, '08b') for byte in data)

def bits_to_bytes(bits):
    return bytes(int(bits[i:i+8], 2) for i in range(0, len(bits), 8))

def embed_file_in_image(image, file_data, filename):
    if len(file_data) > MAX_FILE_SIZE:
        raise ValueError("File too large. Must be under 2MB.")

    file_ext = os.path.splitext(filename)[1]
    metadata = f"{len(file_ext):02d}{file_ext}{len(file_data):08d}"
    metadata_bytes = metadata.encode('utf-8')

    total_data = metadata_bytes + file_data
    bits = bytes_to_bits(total_data)

    available_capacity = image.width * image.height * 3  # 3 bits per pixel (RGB)

    if len(bits) > available_capacity:
        raise ValueError("Image too small to hold the file data. Try a larger image or smaller file.")

    pixels = list(image.getdata())
    new_pixels = []

    bit_index = 0
    for pixel in pixels:
        new_pixel = []
        for channel in pixel[:3]:  # R, G, B
            if bit_index < len(bits):
                new_channel = (channel & ~1) | int(bits[bit_index])
                bit_index += 1
            else:
                new_channel = channel
            new_pixel.append(new_channel)
        if len(pixel) == 4:
            new_pixel.append(pixel[3])  # Preserve alpha
        new_pixels.append(tuple(new_pixel))

    new_image = Image.new(image.mode, image.size)
    new_image.putdata(new_pixels)
    return new_image

def extract_file_from_image(image):
    pixels = list(image.getdata())
    bits = ''
    for pixel in pixels:
        for channel in pixel[:3]:  # Only R, G, B channels
            bits += str(channel & 1)

    byte_data = bits_to_bytes(bits)

    # Read metadata: ext length (2), ext (variable), size (10)
    ext_len = int(byte_data[:2].decode('utf-8'))
    ext = byte_data[2:2+ext_len].decode('utf-8')
    size = int(byte_data[2+ext_len:2+ext_len+8].decode('utf-8'))

    start = 2 + ext_len + 8
    
    file_bytes = byte_data[start:start+size]

    if len(file_bytes) != size:
        raise ValueError("Failed to extract full file. The image may be corrupted or too small.")

    return file_bytes, f"extracted_file{ext}"
