import React, { useState } from "react";
import axios from "axios";
import { useDropzone } from "react-dropzone";
import'./milestonetwo.css'
function MilestoneTwo() {
    const [inputType, setInputType] = useState("salary slip");
    const [extractedData, setExtractedData] = useState(null);
    const [loading, setLoading] = useState(false);
  
    const onDrop = async (files) => {
      const formData = new FormData();
      files.forEach(file => formData.append("files", file));
  
      try {
        setLoading(true);
        const response = await axios.post("http://127.0.0.2:5000/process", formData, {
          headers: {
            "Content-Type": "multipart/form-data",
          },
          params: {
            input_type: inputType,
          },
        });
  
        console.log("Extracted Data:", response.data);
        setExtractedData(response.data);
      } catch (error) {
        console.error("Error processing files:", error);
      } finally {
        setLoading(false);
      }
    };
  
    const { getRootProps, getInputProps } = useDropzone({
      onDrop,
      multiple: true,
      accept: ".jpg, .jpeg, .png, .pdf"
    });
  
  
  
    return (
      <div>
        <h1>OCR Data Extraction from Slips</h1>
        <div>
          <label>Select the slip type: </label>
          <select value={inputType} onChange={(e) => setInputType(e.target.value)}>
            <option value="salary slip">Salary Slip</option>
            <option value="balance slip">Balance Slip</option>
            <option value="cash slip">Cash Slip</option>
          </select>
        </div>
  
        <div {...getRootProps()} className="dropzone">
          <input {...getInputProps()} />
          <p>Drag & drop files here, or click to select files</p>
        </div>
  
        {loading && <p>Processing...</p>}
  
        {extractedData && (
    <div>
      <h2>Extracted Data</h2>
      <div className="extracted-data"style={{overflow:"hidden",margin:"5%"}}>
        {Object.entries(extractedData.extracted_data).map(([fileName, text], index) => (
          <div key={index} className="data-item">
            <h3 style={{color:"black"}}>{fileName}</h3>
            <pre style={{display:"flex",flexWrap:"wrap",textAlign:"initial" }}>{text}</pre>
          </div>
        ))}
      </div>
  
      <h3 style={{marginTop:"5%"}}>Generated Pie Charts</h3>
            <div className="pie-charts" style={{justifyContent:"center",margin:"5%"}}>
              {extractedData.pie_chart_files.map((url, index) => (
                <div key={index} className="pie-chart">
                  <img 
                    src={url} 
                    alt={`Pie Chart ${index + 1}`} 
                    onError={(e) => e.target.style.display = 'none'} // Hide if the image fails to load
                  />
                </div>
              ))}
            </div>
            <h3>Generated bar Charts</h3>
            <div className="pie-charts" style={{justifyContent:"center",margin:"5%"}}>
              {extractedData.bar_chart_files.map((url, index) => (
                <div key={index} className="pie-chart">
                  <img 
                    src={url} 
                    alt={`Bar Chart ${index + 1}`} 
                    onError={(e) => e.target.style.display = 'none'} // Hide if the image fails to load
                  />
                </div>
              ))}
            </div>
          </div>
  
        )}
      </div>
    );
  }
export default MilestoneTwo
