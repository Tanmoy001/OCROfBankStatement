import React, { useState } from 'react';
import axios from 'axios';

function App() {
  const [file, setFile] = useState(null);
  const [upperPercent, setUpperPercent] = useState(0.02);
  const [lowerPercent, setLowerPercent] = useState(0.64);
  const [ocrResults, setOcrResults] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
  };

  const handleSubmit = async () => {
    if (!file) {
      alert("Please upload a file.");
      return;
    }

    setLoading(true);
    const formData = new FormData();
    formData.append("file", file);
    formData.append("upper_percent", upperPercent);
    formData.append("lower_percent", lowerPercent);

    try {
      const response = await axios.post("http://localhost:5000/process_file", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      setOcrResults(response.data);
    } catch (error) {
      console.error("Error during file processing", error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <h1>OCR File Processor</h1>
      <input type="file" onChange={handleFileChange} />
      <div>
        <label>Upper Crop Percentage:</label>
        <input
          type="number"
          value={upperPercent}
          onChange={(e) => setUpperPercent(e.target.value)}
        />
      </div>
      <div>
        <label>Lower Crop Percentage:</label>
        <input
          type="number"
          value={lowerPercent}
          onChange={(e) => setLowerPercent(e.target.value)}
        />
      </div>
      <button onClick={handleSubmit} disabled={loading}>
        {loading ? "Processing..." : "Start OCR"}
      </button>

      {ocrResults && (
        <div>
          <h2>OCR Results</h2>
          <pre>{JSON.stringify(ocrResults, null, 2)}</pre>
        </div>
      )}
    </div>
  );
}

export default App;
