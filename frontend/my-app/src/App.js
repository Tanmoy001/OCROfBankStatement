import React from "react";
import './App.css';
import { BrowserRouter, Routes, Route, Link } from "react-router-dom";
import MilestoneTwo from "./component/Milestonetwo/MilestoneTwo";
import MilestoneOne from "./component/Milestoneone/MilestoneOne";
import Milestonefine from "./component/milestonefinal/Milestonefine";

// Home Component
function Home() {

  return (
    <div className="home" style={{display:"flex",justifyContent:"center", flexDirection:"column"}}>
<h1 style={{ color: "black", fontSize: "xx-large" }}>
  Infosys Springboard Internship 5.0 batch 2.0 ~ 
  <a 
    href="https://tanmoy-chowdhury.netlify.app/" 
    target="_blank" 
    rel="noopener noreferrer" 
    style={{ color: "blue", textDecoration: "underline", cursor: "pointer", textDecorationLine:'none' }}
  >
    Tanmoy Chowdhury
  </a>
</h1>
     <p>
        This project is a part of the Infosys Springboard internship where I am 
        exploring advanced concepts in software development, machine learning, 
        and cloud technologies. Throughout the internship, I have developed 
        hands-on experience working with tools like React, Flask, Cloudinary, and 
        leveraging cloud technologies for deployment and data management.
      </p>
      <p style={{color:'brown',textDecoration:"underline"}}>Explore the milestones below</p>

      <div className="milestone-container">
        
          <div className="milestone-box">
            <h3>OCR and Data Extraction</h3>
            <p>
            Ocr of images includes the implementation of basic file processing and 
              data extraction using OCR technology. It also covers some initial data 
              analysis using machine learning models.
            </p>
            <Link to="/ocr-of-images"><button className="demo-button">Start Demo</button></Link>
          </div>
        

       
          <div className="milestone-box">
            <h3>Salary and Expensies Analysis</h3>
            <p>
            Live financial Data analysis extends the OCR and data processing capabilities, focusing on 
              visualizing data with charts and generating reports from extracted information.
            </p>
            <Link to="/financial-data-analysis"><button className="demo-button">Start Demo</button></Link>
          </div>

          <div className="milestone-box">
            <h3>Financial Data Analysis from cloud</h3>
            <p>
            Live financial Data analysis extends the OCR and data processing capabilities, focusing on 
              visualizing data with charts and generating reports from extracted information.
            </p>
            <Link to="/financial-final"><button className="demo-button">Start Demo</button></Link>
          </div>
      
      </div>

     
    </div>
  );
}

function App() {
  return (
    <div className="App">
      <div className="bg"></div>
      <div className="bg bg2"></div>
      <div className="bg bg3"></div>

      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/ocr-of-images" element={<MilestoneOne />} />
          <Route path="/financial-data-analysis" element={<MilestoneTwo />} />
          <Route path="/financial-final" element={<Milestonefine />} />
        </Routes>
      </BrowserRouter>
    </div>
  );
}

export default App;
