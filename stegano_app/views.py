import os
from django.shortcuts import render
import numpy as np
from .forms import SteganalysisForm
from .forms import ImageUploadForm
from .utils import estimate_capacity
from PIL import Image
from django.conf import settings
from django.http import HttpResponse
from .lsb_utils import embed_file_in_image
from .lsb_utils import extract_file_from_image
import cv2


# Create your views here.
def index(request):
    return render(request, 'index.html')

# def hide_text_in_image(image, text):
#     data = text.encode('utf-8')
#     return stepic.encode(image, data)



def encryption_view(request):
    message = ""
    if request.method == "POST":
        try:
            uploaded_file = request.FILES.get('file')
            image_file = request.FILES.get('image')

            if not uploaded_file or not image_file:
                message = "Please upload both image and file."
            else:
                image = Image.open(image_file)
                if image.mode != 'RGBA':
                    image = image.convert('RGBA')

                file_data = uploaded_file.read()
                filename = uploaded_file.name

                new_image = embed_file_in_image(image, file_data, filename)

                save_dir = os.path.join(settings.MEDIA_ROOT, 'encrypted_images')
                os.makedirs(save_dir, exist_ok=True)
                save_path = os.path.join(save_dir, 'hidden_' + os.path.splitext(image_file.name)[0] + '.png')
                new_image.save(save_path)

                message = "File has been hidden successfully in the image."

        except Exception as e:
            message = f"An error occurred: {e}"

    return render(request, 'encryption.html', {'message': message})


def decryption_view(request):
    if request.method == 'POST':
        try:
            image_file = request.FILES.get('image')
            if not image_file:
                return render(request, 'decryption.html', {'text': "Please upload an image."})

            image = Image.open(image_file)
            if image.mode != 'RGBA':
                image = image.convert('RGBA')

            file_bytes, filename = extract_file_from_image(image)

            if not isinstance(file_bytes, bytes) or not file_bytes:
                raise ValueError("Decoded file data is invalid.")

            response = HttpResponse(file_bytes, content_type='application/octet-stream')
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            return response

        except Exception as e:
            return render(request, 'decryption.html', {'text': f"An error occurred: {e}"})

    return render(request, 'decryption.html')



def steganalysis_view(request):
    # If it's a POST request, handle the form submission
    if request.method == 'POST':
        form = SteganalysisForm(request.POST, request.FILES)
        if form.is_valid():
            # Handle the uploaded image
            uploaded_image = request.FILES['image']
            
            # Save the image temporarily for analysis
            image_path = os.path.join('media', 'uploaded_images', uploaded_image.name)
            with open(image_path, 'wb') as f:
                for chunk in uploaded_image.chunks():
                    f.write(chunk)
            
            # Perform the steganalysis (decode hidden data from the image)
            result = perform_steganalysis(image_path)
            
            # Render the result page
            return render(request, 'steganalyze_result.html', {'result': result})
    else:
        # If it's a GET request, just show the form
        form = SteganalysisForm()

    # Render the steganalysis form page
    return render(request, 'steganalyze.html', {'form': form})


def perform_steganalysis(image_path):
    # ✅ Don't load with cv2 here, just send path
    hidden_message = extract_lsb_message(image_path)

    # Optional: remove temporary file
    os.remove(image_path)

    if "Yes" in hidden_message:
        return f"Yes, hidden message detected: {hidden_message}"
    else:
        return "No hidden message found in the image."

def extract_lsb_message(image_path):
    # Check if image exists before processing
    if not os.path.exists(image_path):
        return "Image not found or invalid path."

    
    img = cv2.imread(image_path)
    if img is None:
        return "Failed to load image. Check if the image format is supported."

    # Convert the image to grayscale (LSB analysis works on single channel)
    gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Extract hidden message from the least significant bits (LSB)
    bits = []
    for row in gray_img:
        for pixel in row:
            bits.append(pixel & 1)

    # Decode the message from bits
    message = ""
    for i in range(0, len(bits), 8):
        byte = bits[i:i+8]
        if len(byte) < 8:
            break
        char = chr(int(''.join(map(str, byte)), 2))
        if char == '\0':
            break
        message += char

    if len(message) == 0:
        return "No hidden message found."

    # Check if the message is meaningful
    printable_chars = sum(c.isprintable() for c in message)
    total_chars = len(message)

    if printable_chars / total_chars > 0.9 and total_chars > 5:
        return "No, hidden message detected."
    else:
        return "Yes hidden message found."



    

def estimate_capacity_view(request):
    estimated_capacity = None
    used_percent = None
    file_size_kb = None
    bar_color = "#4caf50"  # Default green

    if request.method == 'POST':
        form = ImageUploadForm(request.POST, request.FILES)
        if form.is_valid():
            image_file = form.cleaned_data['image']
            data_file = form.cleaned_data.get('data_file')

            # Estimate capacity of image
            image_size_kb, estimated_capacity = estimate_capacity(image_file)

            if data_file:
                file_size_kb = data_file.size / 1024  # KB
                used_percent = round((file_size_kb / estimated_capacity) * 100, 2)

                # Set progress bar color
                if used_percent > 90:
                    bar_color = "#f44336"  # Red
                elif used_percent > 60:
                    bar_color = "#ff9800"  # Orange
                else:
                    bar_color = "#4caf50"  # Green

            return render(request, 'estimate_capacity.html', {
                'form': form,
                'estimated_capacity': estimated_capacity,
                'file_size_kb': round(file_size_kb, 2) if file_size_kb else None,
                'used_percent': used_percent,
                'bar_color': bar_color
            })
    else:
        form = ImageUploadForm()

    return render(request, 'estimate_capacity.html', {
        'form': form
    })
