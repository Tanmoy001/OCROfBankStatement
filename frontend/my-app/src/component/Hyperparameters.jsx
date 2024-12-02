import React from "react";

function Hyperparameters({ params, setParams }) {
  const handleChange = (e) =>
    setParams({ ...params, [e.target.name]: e.target.value });

  return (
    <div>
      <h3>Hyperparameters</h3>
      <label>Upper Crop Percentage: </label>
      <input
        type="number"
        name="upperPercent"
        value={params.upperPercent}
        onChange={handleChange}
        step="0.01"
        min="0"
        max="1"
      />
      <br />
      <label>Lower Crop Percentage: </label>
      <input
        type="number"
        name="lowerPercent"
        value={params.lowerPercent}
        onChange={handleChange}
        step="0.01"
        min="0"
        max="1"
      />
      <br />
      <label>PSM Mode: </label>
      <input
        type="number"
        name="psm"
        value={params.psm}
        onChange={handleChange}
      />
      <br />
      <label>OEM Mode: </label>
      <input
        type="number"
        name="oem"
        value={params.oem}
        onChange={handleChange}
      />
    </div>
  );
}

export default Hyperparameters;
