from flask import Flask, request, jsonify
from flask_cors import CORS
import easyocr
import re
from pdf2image import convert_from_path
from PIL import Image
import io
import pandas as pd
from uuid import uuid4
from langchain.prompts import PromptTemplate
from langchain_groq import ChatGroq
import cloudinary
import cloudinary.uploader
import os
import pandas as pd
from tabulate import tabulate
import shutil
import matplotlib
matplotlib.use('Agg')  # Non-GUI backend for matplotlib
import matplotlib.pyplot as plt
from dotenv import load_dotenv

app = Flask(__name__)
CORS(app)  # Allow cross-origin requests from the React frontend
load_dotenv()

# Initialize EasyOCR Reader
reader = easyocr.Reader(['en'], gpu=True)

# Initialize LLM
llm = ChatGroq(
    temperature=0,
    groq_api_key=os.getenv('GROQ_API_KEY'),
    model_name="llama-3.1-70b-versatile"
)

# Configure Cloudinary using environment variables
cloudinary.config(
    cloud_name=os.getenv('CLOUDINARY_CLOUD_NAME'),
    api_key=os.getenv('CLOUDINARY_API_KEY'),
    api_secret=os.getenv('CLOUDINARY_API_SECRET')
)

# Define cropping limits
CROP_LIMITS = {"upper_percent": 0.00, "lower_percent": 0.00}

def ensure_directory(directory):
    os.makedirs(directory, exist_ok=True)

def crop_percent(image_path, output_path, upper_percent=0.00, lower_percent=0.00):
    try:
        with Image.open(image_path) as img:
            width, height = img.size
            crop_upper = height * upper_percent
            crop_lower = height * (1 - lower_percent)
            cropped_img = img.crop((0, crop_upper, width, crop_lower))

            if cropped_img.mode != 'RGB':
                cropped_img = cropped_img.convert('RGB')

            cropped_img.save(output_path, format="JPEG")
    except Exception as e:
        print(f"Error cropping {image_path}: {e}")

def convert_pdf_to_images(pdf_path, output_folder):
    ensure_directory(output_folder)
    try:
        pages = convert_from_path(pdf_path, dpi=300)
        image_paths = []
        for i, page in enumerate(pages):
            image_path = os.path.join(output_folder, f"{os.path.basename(pdf_path)}_page_{i + 1}.jpg")
            page.save(image_path, "JPEG")
            image_paths.append(image_path)
        return image_paths
    except Exception as e:
        print(f"Error converting {pdf_path} to images: {e}")
        return []

def process_images_with_easyocr(image_paths):
    text_list = []
    for image_path in image_paths:
        try:
            if CROP_LIMITS:
                cropped_path = os.path.join(os.path.dirname(image_path), f"cropped_{os.path.basename(image_path)}")
                crop_percent(image_path, cropped_path, CROP_LIMITS.get("upper_percent"), CROP_LIMITS.get("lower_percent"))
                image_path = cropped_path
            ocr_results = reader.readtext(image_path)
            recognized_text = " ".join([text for _, text, _ in ocr_results])
            text_list.append((image_path, recognized_text))
        except Exception as e:
            print(f"Error processing {image_path}: {e}")
    return text_list

def upload_to_cloudinary(file_data, file_name, folder_path):
    """Upload file data to Cloudinary in the specified folder."""
    try:
        response = cloudinary.uploader.upload(
            file_data,
            folder=folder_path,
            public_id=file_name,
            resource_type="image"
        )
        return response.get('secure_url')
    except Exception as e:
        print(f"Error uploading to Cloudinary: {e}")
        return None


def get_prompt_for_document(input_type, ocr_text):
    """Generate a document-specific prompt for the LLM based on the input type."""
    prompts = {
        "salary slip": "Extract the following from the salary slip : gross salary, house rent allowances, conveyance allowances, net salary, basic amount. Text: {{ocr_text}}",
        "balance slip": "Extract the following from the balance slip: account holder name, account number, balance, date, bank name. Text: {{ocr_text}}",
        "cash slip": "Extract the following from the cash slip: transaction date, amount, transaction ID, bank/ATM ID. Text: {{ocr_text}}"
    }
    return prompts[input_type].replace("{{ocr_text}}", ocr_text)

def extract_data_with_llm(ocr_text, input_type):
    try:
        prompt_text = get_prompt_for_document(input_type, ocr_text)
        prompt = PromptTemplate(input_variables=["ocr_text"], template=prompt_text)
        result = prompt | llm
        response = result.invoke({"ocr_text": ocr_text})
        return response.content
    except Exception as e:
        print(f"Error interacting with LLM: {e}")
        return {"error": str(e)}

def process_user_request(input_paths, input_type):
    """Process user input (image, PDF, or folder) and extract specific data."""
    image_paths = []
    for input_path in input_paths:
        if os.path.isfile(input_path):
            if input_path.lower().endswith(".pdf"):
                output_folder = os.path.join(os.path.dirname(input_path), "pdf_images")
                image_paths.extend(convert_pdf_to_images(input_path, output_folder))
            else:
                image_paths.append(input_path)
        elif os.path.isdir(input_path):
            image_paths.extend([os.path.join(input_path, f) for f in os.listdir(input_path) if f.lower().endswith(('.jpg', '.png', '.jpeg'))])
        else:
            print(f"Invalid input path: {input_path}")
            return []

    ocr_results = process_images_with_easyocr(image_paths)
    extracted_data = {os.path.basename(img): extract_data_with_llm(text, input_type) for img, text in ocr_results}
    return extracted_data

def generate_bar_charts(data, cloudinary_folder):
    """Generate bar charts for attributes and upload them to Cloudinary."""
    try:
        rows = []
        for image, attributes in data.items():
            row = {"Image": image}
            if isinstance(attributes, dict):
                row.update(attributes)
            elif isinstance(attributes, str):
                matches = re.findall(r"(\d+\.\s*[A-Za-z\s]+):\s*([^\n]+)", attributes)
                for key, value in matches:
                    row[key.strip()] = value.strip()
            rows.append(row)

        df = pd.DataFrame(rows)

        bar_chart_urls = []
        for column in df.columns:
            if column == "Image":
                continue

            numerical_data = {}
            for _, row in df.iterrows():
                if pd.notnull(row[column]):
                    match = re.search(r"\d+", str(row[column]))
                    if match:
                        numerical_data[row["Image"]] = int(match.group())

            if numerical_data:
                # Create a bar chart
                plt.figure(figsize=(10, 6))
                plt.bar(numerical_data.keys(), numerical_data.values(), color='skyblue')
                plt.xlabel('Images')
                plt.ylabel(column)
                plt.title(f'{column} Comparison')

                # Save chart to a BytesIO object
                chart_buffer = io.BytesIO()
                plt.savefig(chart_buffer, format="png")
                plt.close()  # Avoid Tkinter-related issues

                # Upload chart to Cloudinary
                chart_buffer.seek(0)
                cloudinary_url = upload_to_cloudinary(chart_buffer, f"{column}_comparison", f"{cloudinary_folder}/bar_charts")
                if cloudinary_url:
                    bar_chart_urls.append(cloudinary_url)

        return bar_chart_urls
    except Exception as e:
        print(f"Error generating bar charts: {e}")
        return []
    

def generate_pie_charts(data, cloudinary_folder):
    """Generate pie charts for attributes and upload them to Cloudinary."""
    try:
        rows = []
        for image, attributes in data.items():
            row = {"Image": image}
            if isinstance(attributes, dict):
                row.update(attributes)
            elif isinstance(attributes, str):
                matches = re.findall(r"(\d+\.\s*[A-Za-z\s]+):\s*([^\n]+)", attributes)
                for key, value in matches:
                    row[key.strip()] = value.strip()
            rows.append(row)

        df = pd.DataFrame(rows)

        pie_chart_urls = []
        for column in df.columns:
            if column == "Image":
                continue

            numerical_data = {}
            for _, row in df.iterrows():
                if pd.notnull(row[column]):
                    match = re.search(r"\d+", str(row[column]))
                    if match:
                        numerical_data[row["Image"]] = int(match.group())

            if numerical_data:
                plt.figure(figsize=(6, 6))
                plt.pie(
                    numerical_data.values(),
                    labels=numerical_data.keys(),
                    autopct="%1.1f%%",
                    startangle=90,
                    colors=plt.cm.Paired.colors
                )
                plt.title(f"{column} Comparison")
                
                # Save chart to a BytesIO object
                chart_buffer = io.BytesIO()
                plt.savefig(chart_buffer, format="png")
                plt.close()  # Avoid Tkinter-related issues

                # Upload chart to Cloudinary
                chart_buffer.seek(0)
                cloudinary_url = upload_to_cloudinary(chart_buffer, f"{column}_comparison", f"{cloudinary_folder}/pie_charts")
                if cloudinary_url:
                    pie_chart_urls.append(cloudinary_url)

        return pie_chart_urls
    except Exception as e:
        print(f"Error generating pie charts: {e}")
        return []

@app.route('/process', methods=['POST'])
def process_files():
    try:
        input_type = request.args.get('input_type')
        files = request.files.getlist("files")

        # Generate a unique folder name for this upload
        unique_folder = f"milestonetwo/{uuid4().hex}"

        # Temporary directories for uploads and pie charts
        upload_dir = "uploads"
        pie_chart_dir = "pie_charts"
        bar_chart_dir = "bar_charts"  # New directory for bar charts

        # Save the uploaded files temporarily
        input_paths = []
        for file in files:
            file_path = os.path.join(upload_dir, file.filename)
            ensure_directory(upload_dir)
            file.save(file_path)
            input_paths.append(file_path)

        # Process the uploaded files
        extracted_data = process_user_request(input_paths, input_type)

        # Generate pie charts and bar charts for attributes
        ensure_directory(pie_chart_dir)
        ensure_directory(bar_chart_dir)
        pie_chart_urls = generate_pie_charts(extracted_data, unique_folder)
        bar_chart_urls = generate_bar_charts(extracted_data, unique_folder)

        # Cleanup local directories (Windows-compatible)
        shutil.rmtree(upload_dir, ignore_errors=True)
        shutil.rmtree(pie_chart_dir, ignore_errors=True)
        shutil.rmtree(bar_chart_dir, ignore_errors=True)

        # Return extracted data and Cloudinary URLs as JSON
        return jsonify({
            "extracted_data": extracted_data,
            "pie_chart_files": pie_chart_urls,
            "bar_chart_files": bar_chart_urls
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.2", port=5001)