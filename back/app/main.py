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

app = Flask(__name__)
CORS(app)

# Configurations
UPLOAD_FOLDER = '../uploads'
PROCESSED_FOLDER = '../processed'
CSV_FILE_NAME = "ocr_results.csv"

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

cloudinary.config(
    cloud_name=os.getenv('CLOUDINARY_CLOUD_NAME'),
    api_key=os.getenv('CLOUDINARY_API_KEY'),
    api_secret=os.getenv('CLOUDINARY_API_SECRET')
)


def is_valid_image(file_path):
    try:
        with Image.open(file_path) as img:
            img.verify()  # Check if the image can be verified
            img = Image.open(file_path)  # Reopen the image for actual processing
            img.load()  # Try to load the image into memory
        return True
    except (IOError, SyntaxError):
        return False


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Tesseract path (adjust as needed)
pytesseract.pytesseract.tesseract_cmd = "C:\\Program Files\\Tesseract-OCR\\tesseract.exe"

def pdf_to_images(pdf_path, output_dir):
    images = []
    pdf_doc = fitz.open(pdf_path)
    for page_num in range(len(pdf_doc)):
        page = pdf_doc[page_num]
        pix = page.get_pixmap()
        img_path = os.path.join(output_dir, f"page_{page_num + 1}.png")
        pix.save(img_path)
        images.append(img_path)
    pdf_doc.close()
    return images

def crop_percent(image_path, output_path, upper_percent=0.0, lower_percent=0.0):
    with Image.open(image_path) as img:
        # Convert the image to RGB if it's in a different mode
        if img.mode != 'RGB':
            img = img.convert('RGB')  # Convert to RGB mode if needed
        
        width, height = img.size
        crop_upper = height * upper_percent
        crop_lower = height * (1 - lower_percent)
        box = (0, crop_upper, width, crop_lower)
        cropped_img = img.crop(box)

        cropped_img.save(output_path, format="JPEG")

def fetch_images_from_folder(folder_name):
    try:
        response = cloudinary.api.resources(
            type="upload",
            prefix=folder_name,  # Folder path in Cloudinary
            max_results=50  # Adjust based on your needs
        )
        # Extract URLs
        image_urls = [resource['secure_url'] for resource in response['resources']]
        return image_urls
    except Exception as e:
        print(f"Error fetching images: {e}")
        return []
    
import mimetypes

def upload_to_cloudinary(file_path, folder="processed_files"):
    """Upload file to Cloudinary and return the URL."""
    try:
        # Check MIME type of the file
        mime_type, _ = mimetypes.guess_type(file_path)
        
        # Allow all file types for upload
        if mime_type is None:
            print(f"Warning: MIME type could not be determined for file {file_path}")

        # Proceed with Cloudinary upload
        response = cloudinary.uploader.upload(file_path, folder=folder, resource_type="auto")
        if response.get("error"):
            raise Exception(response["error"]["message"])
        return response.get("url")
    except Exception as e:
        print(f"Error uploading to Cloudinary: {e}")
        raise

@app.route("/")
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
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

        try:
            file.save(file_path)
            print(f"File {filename} uploaded successfully at {file_path}")
            
            # Validate image file before uploading
            if not is_valid_image(file_path):
                return jsonify({'error': 'Invalid image file'}), 400

            # Check the MIME type of the file
            mime_type, _ = mimetypes.guess_type(file_path)
            print(f"File MIME type: {mime_type}")

            # Upload file to Cloudinary
            file_url = upload_to_cloudinary(file_path, folder="uploaded_files")
            return jsonify({'message': f'File {filename} uploaded successfully!', 'file_url': file_url}), 200
        except Exception as e:
            print(f"Error saving file: {e}")
            return jsonify({'error': 'Error saving file'}), 500
    else:
        return jsonify({'error': 'Invalid file type'}), 400

import uuid
from datetime import datetime
import shutil

@app.route("/process", methods=["POST"])
def process_file():
    data = request.json
    file_url = data.get("file_url")
    crop_params = data.get("crop_params", {"upper_percent": 0.0, "lower_percent": 0.0})
    max_cropped_images = data.get("max_cropped_images", 10)
    tesseract_params = data.get("tesseract_params", {"psm": 3, "oem": 3})
    easyocr_params = data.get("easyocr_params", {"languages": ["en"], "gpu": True})

    unique_id = str(uuid.uuid4())
    output_dir = os.path.join(PROCESSED_FOLDER, unique_id)
    cropped_dir = os.path.join(output_dir, "cropped_images")
    tesseract_dir = os.path.join(output_dir, "tesseract_images")
    easyocr_dir = os.path.join(output_dir, "easyocr_images")

    os.makedirs(cropped_dir, exist_ok=True)
    os.makedirs(tesseract_dir, exist_ok=True)
    os.makedirs(easyocr_dir, exist_ok=True)

    # Download the file
    file_path = f"{output_dir}/{os.path.basename(file_url)}"
    os.system(f"curl -o {file_path} {file_url}")

    if file_path.endswith(".pdf"):
        image_paths = pdf_to_images(file_path, cropped_dir)[:max_cropped_images]
    else:
        image_paths = [file_path]

    results = []
    for image_path in image_paths:
        cropped_path = os.path.join(cropped_dir, f"cropped_{os.path.basename(image_path)}")
        crop_percent(image_path, cropped_path, **crop_params)

        # Tesseract OCR
        tesseract_path = os.path.join(tesseract_dir, f"tesseract_{os.path.basename(image_path)}")
        with Image.open(cropped_path) as img:
            draw = ImageDraw.Draw(img)
            tesseract_config = f"--psm {tesseract_params['psm']} --oem {tesseract_params['oem']}"
            tesseract_data = pytesseract.image_to_data(cropped_path, config=tesseract_config, output_type=pytesseract.Output.DICT)
            for i, text in enumerate(tesseract_data["text"]):
                if text.strip():
                    x, y, w, h = (tesseract_data["left"][i], tesseract_data["top"][i],
                                  tesseract_data["width"][i], tesseract_data["height"][i])
                    draw.rectangle([x, y, x + w, y + h], outline="red", width=2)
                    results.append({
                        "Recognized Text": text.strip(),
                        "Confidence Score": tesseract_data["conf"][i],
                        "OCR Model": "Tesseract"
                    })
            img.save(tesseract_path)

        # EasyOCR
        easyocr_path = os.path.join(easyocr_dir, f"easyocr_{os.path.basename(image_path)}")
        with Image.open(cropped_path) as img:
            draw = ImageDraw.Draw(img)
            reader = easyocr.Reader(easyocr_params["languages"], gpu=easyocr_params["gpu"])
            easyocr_results = reader.readtext(cropped_path)
            for bbox, text, prob in easyocr_results:
                draw.rectangle([tuple(bbox[0]), tuple(bbox[2])], outline="blue", width=2)
                results.append({
                    "Recognized Text": text.strip(),
                    "Confidence Score": prob * 100,
                    "OCR Model": "EasyOCR"
                })
            img.save(easyocr_path)

    # (Rest of the code for uploading to Cloudinary and returning the response remains the same)


    # Upload processed images to Cloudinary
    tesseract_image_urls = [upload_to_cloudinary(os.path.join(tesseract_dir, img), folder=f"processed_files/{unique_id}/tesseract")
                            for img in os.listdir(tesseract_dir)]
    easyocr_image_urls = [upload_to_cloudinary(os.path.join(easyocr_dir, img), folder=f"processed_files/{unique_id}/easyocr")
                          for img in os.listdir(easyocr_dir)]

    # Save results to CSV
    results_df = pd.DataFrame(results)
    results_csv_path = os.path.join(output_dir, CSV_FILE_NAME)
    results_df.to_csv(results_csv_path, index=False)

    # Upload CSV to Cloudinary
    csv_url = upload_to_cloudinary(results_csv_path, folder=f"processed_files/{unique_id}/csv_file")

    return jsonify({
        "message": "Processing complete",
        "results_csv_url": csv_url,
        "tesseract_image_urls": tesseract_image_urls,
        "easyocr_image_urls": easyocr_image_urls,
        "ocr_results": results
    }), 200

@app.route('/api/images', methods=['GET'])
def get_images():
    folder_name = 'processed_files/{unique_id}'  # Replace with your Cloudinary folder name
    images = fetch_images_from_folder(folder_name)
    return jsonify({'images': images})


if __name__ == "__main__":
    app.run(debug=True)
