# OCR of bank statement 
### A system to automate the management of financial documents by fetching, processing, and storing them efficiently using OCR and cloud-based technologies.

## Features
### Milestone 1: Fetching and Image Quality
Web Scraping: Download PDFs and images from websites.
Image Quality Check: Ensure a minimum of 300 DPI for financial documents (e.g., bank checks).
Cloud Integration: Upload/download images from Cloudinary.
### Milestone 2: OCR Processing
OCR Engines: Process text using Tesseract and EasyOCR.
File Types: Supports PDF (converted to images) and image formats (jpg, png, etc.).
Cloud Storage: Store uploaded and processed files in Cloudinary.
CSV Export: Save OCR results as CSV files for analysis.
### Milestone 3: Data Extraction and Visualization
Financial Data Extraction: Extract structured data from salary slips, balance slips, etc., using OCR and an LLM.
Data Visualization: Generate pie and bar charts for extracted data using Matplotlib.
Responsive Web App: Built with ReactJS (frontend) and Flask (backend).
Technologies
### Milestone 4: Automatic Data Extraction and Visualization From Cloud
Automatic Financial Data Extraction from cloud: Extract structured data from salary slips, balance slips, etc., using OCR and an LLM and cloudinary.
Data Visualization: Generate pie and bar charts for extracted data using Matplotlib.
Responsive Web App: Built with ReactJS (frontend) and Flask (backend).
Technologies
### Backend: 
##### Flask, Python (requests, BeautifulSoup, PIL, EasyOCR, Tesseract).
### Frontend:
##### ReactJS.
### Cloud:
##### Cloudinary for storage.
### Data Visualization:
##### Matplotlib for charts.
## How to run
##### Frontend:
npm run start
##### Backend:
python MilestoneTwo.py(Default host:127.0.0:5001)
python MilestoneThree.py(Default host:127.0.1:5001)
python MilestoneFour.py(Default host:127.0.2:5001)