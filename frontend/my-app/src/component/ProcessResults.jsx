import React from "react";

const ProcessResults = ({ processedFiles, csvUrl }) => {
  return (
    <div>
      {processedFiles.length > 0 && (
        <div>
          <h2>Processed Files</h2>
          <div style={{ display: "flex", flexWrap: "wrap" }}>
            {processedFiles.map((file, index) => (
              <div key={index} style={{ margin: "10px" }}>
                  <img src={file.image_url} alt={`Processed file ${index + 1}`}
                  style={{ width: "300px", height: "auto" }}
                />
                <p>{file.text}</p>
                <p>Confidence: {file.confidence}%</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {csvUrl && (
        <div>
          <h2>Download Results</h2>
          <a href={csvUrl} download="ocr_results.csv">
            <button>Download CSV</button>
          </a>
        </div>
      )}
    </div>
  );
};

export default ProcessResults;
