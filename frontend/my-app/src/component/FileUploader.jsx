import React from "react";
import { useDropzone } from "react-dropzone";

const FileUploader = ({ onFileUpload }) => {
  const { getRootProps, getInputProps } = useDropzone({
    accept: ".png, .jpg, .jpeg, .gif, .pdf",
    onDrop: (acceptedFiles) => onFileUpload(acceptedFiles[0]),
  });

  return (
    <div {...getRootProps()} className="dropzone">
      <input {...getInputProps()} />
      <p>Drag & drop a file here, or click to select a file</p>
    </div>
  );
};

export default FileUploader;
