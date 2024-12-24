import React, { useState } from 'react';
import axios from 'axios';
import'./milestoneone.css'
function MilestoneOne() {
    const [file, setFile] = useState(null); // State to store the selected file
    const [processedImages, setProcessedImages] = useState([]); // State to store processed images
    const [ocrResults, setOcrResults] = useState(null); // State to store OCR results
    const [loading, setLoading] = useState(false); // Loading indicator
    const [error, setError] = useState(null); // Error message
    const [fileName, setFileName] = useState("No file chosen");
    const [previewImage, setPreviewImage] = useState(null);
  
    const [hyperparameters, setHyperparameters] = useState({
      upperPercent: 0.0,
      lowerPercent: 0.0,
      maxCroppedImages: 10,
      tesseractPsm: 3,
      tesseractOem: 3,
      easyocrGpu: true,
      easyocrLanguages: ["en"],
    });
  
    const handleFileChange = (event) => {
      const selectedFile = event.target.files[0];
      setFile(selectedFile);
      setFileName(selectedFile ? selectedFile.name : "No file chosen");
      setPreviewImage(selectedFile ? URL.createObjectURL(selectedFile) : null);
    };
  
    const handleSliderChange = (name, value) => {
      setHyperparameters((prev) => ({ ...prev, [name]: value }));
    };
  
    const handleToggle = (name) => {
      setHyperparameters((prev) => ({ ...prev, [name]: !prev[name] }));
    };
  
  
    const handleFileUpload = async () => {
      if (!file) {
        setError("Please select a file to upload.");
        return;
      }
  
      setError(null);
      setLoading(true);
  
      try {
        // Step 1: Upload the file
        const formData = new FormData();
        formData.append('file', file);
  
        const uploadResponse = await axios.post(
          'http://127.0.0.1:5001/api/upload',
          formData,
          {
            headers: {
              'Content-Type': 'multipart/form-data',
            },
          }
        );
  
        const fileUrl = uploadResponse.data.file_url;
  
        // Step 2: Process the file
        const processResponse = await axios.post(
          'http://127.0.0.1:5001/process',
          {
            file_url: fileUrl,
            crop_params: {
              upper_percent: hyperparameters.upperPercent,
              lower_percent: hyperparameters.lowerPercent,
            },
          }
        );
  
        const { tesseract_image_urls, easyocr_image_urls, ocr_results } = processResponse.data;
  
        // Combine all image URLs
        setProcessedImages([...tesseract_image_urls, ...easyocr_image_urls]);
        setOcrResults(ocr_results); // Store OCR results
      } catch (err) {
        console.error('Error during file processing:', err);
        setError('An error occurred during file processing.');
      } finally {
        setLoading(false);
      }
    };
  
    const convertToCSV = (data) => {
      const headers = Object.keys(data[0]);
      const rows = data.map((item) => headers.map((header) => item[header]).join(','));
      return [headers.join(','), ...rows].join('\n');
    };
  
    const downloadCSV = (data) => {
      const csv = convertToCSV(data);
      const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
      const link = document.createElement('a');
      const url = URL.createObjectURL(blob);
  
      link.setAttribute('href', url);
      link.setAttribute('download', 'ocr_results.csv');
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);
    };
  
    return (
      <div style={{ padding: '20px', fontFamily: 'Arial, sans-serif' }} >
        <h1 style={{ color: 'white' }}>OCR File Processor</h1>
        
        <p>A project of Springboard 5.0 batch 2.0 ~ Tanmoy Chowdhury</p>
  
        {/* File upload section */}
        <div style={{ display: 'flex', justifyContent: 'center',  gap: '1.5rem', padding:'2rem' }}>
          <div className="file-upload" style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
            <label htmlFor="file-input" className="custom-file-label">
              Choose File
            </label>
            <input type="file" id="file-input" onChange={handleFileChange} style={{ display: 'none' }} />
            <span className="file-name">{fileName}</span>
          </div>
          <button onClick={handleFileUpload} disabled={loading}>
            {loading ? 'Processing...' : 'Upload & Process'}
          </button>
        </div>
  
  
        {error && <p style={{ color: "red" }}>{error}</p>}
        {previewImage && <>
          <div className="options_settings"  style={{display: 'grid',gridTemplateColumns: '1fr 1fr',gap: '1rem',overflow: 'hidden',}}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent:'center'}}>
          <img
                src={previewImage}
                alt="Preview"
                style={{ maxWidth: "100%", maxHeight: "300px", borderRadius: "5px" }}
              />
              </div>
        <div className="hyperparameters">
        <div className="right-panel">
          <h3>Hyperparameters</h3>
          <div className="slider">
            <label>Upper Crop %: {hyperparameters.upperPercent.toFixed(2)}</label>
            <input
              type="range"
              min="0"
              max="1"
              step="0.01"
              value={hyperparameters.upperPercent}
              onChange={(e) => handleSliderChange("upperPercent", parseFloat(e.target.value))}
            />
          </div>
          <div className="slider">
            <label>Lower Crop %: {hyperparameters.lowerPercent.toFixed(2)}</label>
            <input
              type="range"
              min="0"
              max="1"
              step="0.01"
              value={hyperparameters.lowerPercent}
              onChange={(e) => handleSliderChange("lowerPercent", parseFloat(e.target.value))}
            />
          </div>
          <div className="slider">
            <label>Max Cropped Images: {hyperparameters.maxCroppedImages}</label>
            <input
              type="range"
              min="1"
              max="20"
              value={hyperparameters.maxCroppedImages}
              onChange={(e) => handleSliderChange("maxCroppedImages", parseInt(e.target.value))}
            />
          </div>
          <div className="slider">
            <label>Tesseract PSM: {hyperparameters.tesseractPsm}</label>
            <input
              type="range"
              min="0"
              max="13"
              value={hyperparameters.tesseractPsm}
              onChange={(e) => handleSliderChange("tesseractPsm", parseInt(e.target.value))}
            />
          </div>
          <div className="slider">
            <label>Tesseract OEM: {hyperparameters.tesseractOem}</label>
            <input
              type="range"
              min="0"
              max="3"
              value={hyperparameters.tesseractOem}
              onChange={(e) => handleSliderChange("tesseractOem", parseInt(e.target.value))}
            />
          </div>
          <div className="toggle">
            <label>Use GPU for EasyOCR:</label>
            <input
              type="checkbox"
              checked={hyperparameters.easyocrGpu}
              onChange={() => handleToggle("easyocrGpu")}
            />
          </div>
          {/* Add remaining sliders and toggles similarly */}
        </div>
        </div>
        </div>
        </>
      }
    {/* Display processed images */}
    {processedImages.length > 0 && (
          <div style={{paddingBottom:'5rem'}}>
            <h2 style={{padding:'1rem'}}>Processed Images</h2>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '10px', justifyContent:'center', alignItems:'center' }}>
              {processedImages.map((url, index) => (
                <div key={index} style={{display:'contents'}}>
                  <img
                    src={url}
                    alt={`Processed ${index}`}
                    style={{
                      width: '40%',
                      height: 'auto',
                      borderRadius: '5px',
                      boxShadow: '0 4px 8px rgba(0, 0, 0, 0.1)',
                    }}
                  />
                </div>
              ))}
            </div>
          </div>
        )}
  
  
        {/* Download CSV */}
        {ocrResults && (
          <div>
            <button onClick={() => downloadCSV(ocrResults)}>Download OCR Results as CSV</button>
          </div>
        )}
      </div>
    );
  };
export default MilestoneOne
