import React, { useState } from "react";
import axios from "axios";
import './milestone.css';

function Milestonefine() {
  const [inputType, setInputType] = useState("salary slip");
  const [numImages, setNumImages] = useState(10);
  const [extractedData, setExtractedData] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleProcess = async () => {
    setLoading(true);
    try {
      const response = await axios.post("http://localhost:5000/process", {
        folder_name: inputType,
        num_images: numImages,
        input_type: inputType,
      });
      console.log(response)
      setExtractedData(response.data);
    } catch (error) {
      console.error("Error processing images:", error);
    }
    setLoading(false);
  };

  // Helper function to convert extracted data into CSV format
  const generateCSV = (data) => {
    let csvContent = "Image Name,Label,Value\n"; // CSV headers

    Object.keys(data).forEach((imageKey) => {
      const extractedText = data[imageKey];
      const rows = extractedText.split("\n").filter((row) => row.trim() !== "");

      rows.forEach((row) => {
        const [label, value] = row.split(":");
        if (label && value) {
          csvContent += `"${imageKey}","${label.trim()}","${value.trim()}"\n`;
        }
      });
    });

    return csvContent;
  };

  // Helper function to trigger the download of the CSV file
  const downloadCSV = () => {
    const csvData = generateCSV(extractedData.extracted_data || {});
    const blob = new Blob([csvData], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.setAttribute("href", url);
    a.setAttribute("download", "extracted_data.csv");
    a.click();
    URL.revokeObjectURL(url); // Cleanup the URL object
  };

  // Helper function to convert the extracted data into a structured format for display
  const formatData = (data) => {
    return Object.keys(data).map((imageKey) => {
      const extractedText = data[imageKey];
      const rows = extractedText.split("\n").filter((row) => row.trim() !== "");

      const formattedRows = rows.map((row) => {
        const [label, value] = row.split(":");
        return { label: label?.trim(), value: value?.trim() };
      });

      return { imageName: imageKey, data: formattedRows };
    });
  };

  return (
    <div className="App">
      <h1>OCR Data Extraction from Slips</h1>
      
      <label>
        Select the slip type:
        <select value={inputType} onChange={(e) => setInputType(e.target.value)}>
          <option value="salary slip">Salary Slip</option>
          <option value="balance slip">Balance Slip</option>
          <option value="cash slip">Cash Slip</option>
        </select>
      </label>

      <label>
        Select the number of images:
        <input
          type="number"
          min="1"
          max="50"
          value={numImages}
          onChange={(e) => setNumImages(e.target.value)}
        />
      </label>

      <button onClick={handleProcess} disabled={loading}>
        {loading ? "Processing..." : "Process and Fetch"}
      </button>

      {extractedData && (
        <div>
          <h2>Extracted Data</h2>
          <div className="extracted-data" style={{ overflow: "hidden", margin: "5%" }}>
            {formatData(extractedData.extracted_data || {}).map((imageData, index) => (
              <div key={index} className="data-item">
                <h3 style={{ color: "black" }}>{imageData.imageName}</h3>
                <table border="1" style={{ width: "100%", marginTop: "10px", borderCollapse: "collapse" }}>
                  <thead>
                    <tr>
                      <th style={{ padding: "8px", textAlign: "left" }}>Label</th>
                      <th style={{ padding: "8px", textAlign: "left" }}>Value</th>
                    </tr>
                  </thead>
                  <tbody>
                    {imageData.data.map((row, rowIndex) => (
                      <tr key={rowIndex}>
                        <td style={{ padding: "8px" }}>{row.label}</td>
                        <td style={{ padding: "8px" }}>{row.value}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ))}
          </div>

          <h3 style={{ marginTop: "5%" }}>Generated Pie Charts</h3>
          <div className="pie-charts" style={{ justifyContent: "center", margin: "5%" }}>
            {(extractedData.pie_chart_files || []).map((url, index) => (
              <div key={index} className="pie-chart">
                <img
                  src={url}
                  alt={`Pie Chart ${index + 1}`}
                  onError={(e) => (e.target.style.display = "none")} // Hide if the image fails to load
                />
              </div>
            ))}
          </div>

          <h3>Generated Bar Charts</h3>
          <div className="pie-charts" style={{ justifyContent: "center", margin: "5%" }}>
            {(extractedData.bar_chart_files || []).map((url, index) => (
              <div key={index} className="pie-chart">
                <img
                  src={url}
                  alt={`Bar Chart ${index + 1}`}
                  onError={(e) => (e.target.style.display = "none")} // Hide if the image fails to load
                />
              </div>
            ))}
          </div>

          {/* Download CSV Button */}
          <button onClick={downloadCSV} style={{ marginTop: "20px",marginBottom:"20px" }}>
            Download CSV
          </button>
        </div>
      )}
    </div>
  );
}

export default Milestonefine;
