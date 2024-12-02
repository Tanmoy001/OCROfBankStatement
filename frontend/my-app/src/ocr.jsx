import React, { useState } from "react";
import axios from "axios";

const OCRApp = () => {
  const [file, setFile] = useState(null);
  const [upperPercent, setUpperPercent] = useState(0.02);
  const [lowerPercent, setLowerPercent] = useState(0.64);
  const [psm, setPsm] = useState(6);
  const [oem, setOem] = useState(3);
  const [groundTruth, setGroundTruth] = useState("");
  const [results, setResults] = useState(null);

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!file) {
      alert("Please upload a file");
      return;
    }

    const formData = new FormData();
    formData.append("file", file);
    formData.append("upper_percent", upperPercent);
    formData.append("lower_percent", lowerPercent);
    formData.append("psm", psm);
    formData.append("oem", oem);
    formData.append("ground_truth", groundTruth);

    try {
      const response = await axios.post("http://localhost:8000/process", formData);
      setResults(response.data.results);
    } catch (error) {
      console.error("Error processing file:", error);
    }
  };

  return (
    <div>
      <h1>OCR Processing Tool</h1>
      <form onSubmit={handleSubmit}>
        <input type="file" onChange={handleFileChange} accept=".pdf,.png,.jpg,.jpeg" />
        <div>
          <label>Upper Crop Percentage: </label>
          <input
            type="number"
            value={upperPercent}
            onChange={(e) => setUpperPercent(e.target.value)}
          />
        </div>
        <div>
          <label>Lower Crop Percentage: </label>
          <input
            type="number"
            value={lowerPercent}
            onChange={(e) => setLowerPercent(e.target.value)}
          />
        </div>
        <div>
          <label>Tesseract PSM Mode: </label>
          <input
            type="number"
            value={psm}
            onChange={(e) => setPsm(e.target.value)}
          />
        </div>
        <div>
          <label>Tesseract OEM Mode: </label>
          <input
            type="number"
            value={oem}
            onChange={(e) => setOem(e.target.value)}
          />
        </div>
        <div>
          <label>Ground Truth Text: </label>
          <textarea
            value={groundTruth}
            onChange={(e) => setGroundTruth(e.target.value)}
          ></textarea>
        </div>
        <button type="submit">Process</button>
      </form>
      {results && (
        <div>
          <h2>Results</h2>
          <pre>{JSON.stringify(results, null, 2)}</pre>
        </div>
      )}
    </div>
  );
};

export default OCRApp;
