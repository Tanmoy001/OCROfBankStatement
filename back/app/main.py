from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
from flask_cors import CORS
import os
from PIL import Image, ImageDraw
import pytesseract
import fitz  # PyMuPDF
import easyocr
import pandas as pd
import cloudinary
import cloudinary.uploader
import cloudinary.api
import mimetypes
from io import BytesIO
import uuid
import requests
import numpy as np

app = Flask(__name__)
CORS(app)

# Configurations
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf'}

cloudinary.config(
    cloud_name='dtzgf02tl',
    api_key='967163288576492',
    api_secret='4r_cghe2qp0RSWFdjFkToZ5kIko'
)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Tesseract path (adjust as needed)
pytesseract.pytesseract.tesseract_cmd = "C:\\Program Files\\Tesseract-OCR\\tesseract.exe"

def pdf_to_images(pdf_content):
    images = []
    pdf_doc = fitz.open(stream=pdf_content, filetype="pdf")
    for page_num in range(len(pdf_doc)):
        page = pdf_doc.load_page(page_num)
        pix = page.get_pixmap()
        img_bytes = BytesIO(pix.tobytes("png"))
        images.append(img_bytes)
    pdf_doc.close()
    return images

def crop_image(image, upper_percent=0.0, lower_percent=0.0):
    width, height = image.size
    max_size = 1024  # Adjust as needed
    if max(width, height) > max_size:
        ratio = max_size / max(width, height)
        new_width = int(width * ratio)
        new_height = int(height * ratio)
        image = image.resize((new_width, new_height), Image.ANTIALIAS)
    upper_crop = int(height * upper_percent)
    lower_crop = int(height * lower_percent)
    return image.crop((0, upper_crop, width, height - lower_crop))

def upload_to_cloudinary(file_obj, folder):
    try:
        file_name = "file.png"  # Customize this if needed
        response = cloudinary.uploader.upload(file_obj, folder=folder, public_id=file_name, resource_type="auto")
        if response.get("error"):
            raise Exception(response["error"]["message"])
        return response.get("secure_url")
    except Exception as e:
        print(f"Error uploading to Cloudinary: {e}")
        raise

@app.route('/')
def home():
    return jsonify({"message": "Hello from Flask on Vercel!"})

@app.route('/api/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if file and allowed_file(file.filename):
        try:
            file_url = upload_to_cloudinary(file, folder="uploaded_files")
            return jsonify({'message': f'File {file.filename} uploaded successfully!', 'file_url': file_url}), 200
        except Exception as e:
            print(f"Error uploading file: {e}")
            return jsonify({'error': 'Error uploading file'}), 500
    else:
        return jsonify({'error': 'Invalid file type'}), 400

@app.route("/process", methods=["POST"])
def process_file():
    data = request.json
    file_url = data.get("file_url")
    crop_params = data.get("crop_params", {"upper_percent": 0.0, "lower_percent": 0.0})
    tesseract_params = data.get("tesseract_params", {"psm": 3, "oem": 3})
    easyocr_params = data.get("easyocr_params", {"languages": ["en"], "gpu": True})

    unique_id = str(uuid.uuid4())
    results = []

    # Download the file
    response = requests.get(file_url)
    response.raise_for_status()
    file_content = BytesIO(response.content)

    # Process file
    if file_url.endswith(".pdf"):
        image_paths = pdf_to_images (file_content)
    else:
        image_paths = [Image.open(file_content)]

    for img in image_paths:
        cropped_img = crop_image(img, **crop_params)

        # Tesseract OCR
        tesseract_draw = ImageDraw.Draw(cropped_img)
        tesseract_config = f"--psm {tesseract_params['psm']} --oem {tesseract_params['oem']}"
        tesseract_data = pytesseract.image_to_data(cropped_img, config=tesseract_config, output_type=pytesseract.Output.DICT)
        for i, text in enumerate(tesseract_data["text"]):
            if text.strip():
                x, y, w, h = (tesseract_data["left"][i], tesseract_data["top"][i],
                              tesseract_data["width"][i], tesseract_data["height"][i])
                x1 = x + w
                y1 = y + h
                tesseract_draw.rectangle([x, y, x1, y1], outline="red", width=2)
                results.append({
                    "Recognized Text": text.strip(),
                    "Confidence Score": tesseract_data["conf"][i],
                    "OCR Model": "Tesseract"
                })

        tesseract_image_bytes = BytesIO()
        optimized_img = cropped_img.resize((cropped_img.width // 2, cropped_img.height // 2), Image.Resampling.LANCZOS)
        optimized_img.save(tesseract_image_bytes, format="PNG", quality=85)
        tesseract_image_bytes.seek(0)
        tesseract_url = upload_to_cloudinary(tesseract_image_bytes, folder=f"processed_files/{unique_id}/tesseract")

        # EasyOCR
        easyocr_bytes = BytesIO()
        cropped_img.save(easyocr_bytes, format="PNG")
        easyocr_bytes.seek(0)
        easyocr_np = np.array(Image.open(easyocr_bytes))

        easyocr_draw = ImageDraw.Draw(cropped_img)
        reader = easyocr.Reader(easyocr_params["languages"], gpu=easyocr_params["gpu"])
        easyocr_results = reader.readtext(easyocr_np)
        for bbox, text, prob in easyocr_results:
            easyocr_draw.rectangle([tuple(bbox[0]), tuple(bbox[2])], outline="blue", width=2)
            results.append({
                "Recognized Text": text.strip(),
                "Confidence Score": prob * 100,
                "OCR Model": "EasyOCR"
            })

        easyocr_image_bytes = BytesIO()
        cropped_img.save(easyocr_image_bytes, format="PNG")
        easyocr_image_bytes.seek(0)
        easyocr_url = upload_to_cloudinary(easyocr_image_bytes, folder=f"processed_files/{unique_id}/easyocr")

    # Save results to CSV in memory
    results_df = pd.DataFrame(results)
    results_csv_bytes = BytesIO()
    results_df.to_csv(results_csv_bytes, index=False)
    results_csv_bytes.seek(0)
    csv_url = upload_to_cloudinary(results_csv_bytes, folder=f"processed_files/{unique_id}/csv_file")

    # Limit the number of results returned
    summary_results = results[:10]  # Return only the first 10 results

    return jsonify({
        "message": "Processing complete",
        "results_csv_url": csv_url,
        "tesseract_image_urls": [tesseract_url],
        "easyocr_image_urls": [easyocr_url],
        "ocr_results": summary_results
    }), 200

if __name__ == "__main__":
    app.run(debug=True)