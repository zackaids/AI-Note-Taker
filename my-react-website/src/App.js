import React, { useState } from 'react';
import './App.css';
import AWS from 'aws-sdk';

function App() {
  const [selectedFile, setSelectedFile] = useState(null);
  const [downloadType, setDownloadType] = useState('.pdf');

  const handleFileUpload = async (event) => {
    const file = event.target.files[0]; // Get the uploaded file

    if (file) {
      try {
        // Initialize AWS S3 client
        const s3 = new AWS.S3({
          accessKeyId: "accessKeyId", // Use environment variables
          secretAccessKey: "secretAccessKey",
          region: 'us-east-1', // Specify the region of your S3 bucket
        }); 

        // Upload parameters
        const params = {
          Bucket: 'audioinputs',
          Key: file.name,
          Body: file,
          ACL: 'public-read' // Set the ACL to public-read if you want the file to be publicly accessible
        };

        // Upload the file to S3
        const data = await s3.upload(params).promise();
        console.log('File uploaded successfully:', data.Location);
      } catch (error) {
        console.error('Error uploading file:', error);
      }
    }
  };

  const handleDownload = async () => {
    // Initialize AWS S3 client
    const s3 = new AWS.S3({
      accessKeyId: "accessKeyID", // Use environment variables
      secretAccessKey: "secretAccessKey",
      region: 'us-east-1', // Specify the region of your S3 bucket
    });

    try {
      // List objects in the bucket
      const data = await s3.listObjectsV2({ Bucket: 'finalnotes' }).promise();
      
      // Sort objects by LastModified in descending order
      const sortedObjects = data.Contents.sort((a, b) => b.LastModified - a.LastModified);
      
      // Get the key of the most recently modified file
      const mostRecentKey = sortedObjects[0].Key;
  
      // Get the file from S3
      const response = await s3.getObject({
        Bucket: 'finalnotes',
        Key: mostRecentKey,
      }).promise();
  
      // Create a Blob object from the response data
      const blob = new Blob([response.Body], { type: response.ContentType });
  
      // Create a temporary URL for the Blob object
      const url = window.URL.createObjectURL(blob);
  
      // Create a temporary anchor element to trigger the download
      const a = document.createElement('a');
      a.href = url;
      a.download = mostRecentKey; // Set the download filename to the original file name
      document.body.appendChild(a);
      a.click();
  
      // Clean up
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (error) {
      console.error('Error downloading file:', error);
    }
  };

  return (
    <div className="App">
      <nav className="navbar">
        <ul className="nav-links">
        <li><a href="#home">Home</a></li>
          <li><a href="/about">About</a></li> {/* Link to About Us page */}
        </ul>
      </nav>
      <header className="App-header">
        <h1>Audio to Notes Converter</h1>
        <div>
          <input
            id="fileInput"
            type="file"
            style={{ display: 'none' }}
            accept=".mp3,.mp4" // Restrict to .mp3 and .mp4 files
            onChange={handleFileUpload} // Call handleFileUpload function on file selection
          />
          <button onClick={() => document.getElementById('fileInput').click()} className="upload-button">
            Upload Audio/Video File
          </button>
          <button onClick={handleDownload} className="download-button">
            Download
          </button>
        </div>
      </header>
    </div>
  );
  
}

export default App;
