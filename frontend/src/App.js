import React, { useState, useRef } from 'react';


function App() {
  const [selectedFile, setSelectedFile] = useState(null);
  const [imageURL, setImageURL] = useState(null);
  const [error, setError] = useState('');
  const canvasRef = useRef(null);

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    setSelectedFile(file);
    if (file) {
      setImageURL(URL.createObjectURL(file));
    }
  };

  const handleUpload = async () => {
    if (!selectedFile) {
      setError('No file selected');
      return;
    }

    try {
      const formData = new FormData();
      formData.append('image', selectedFile);

      const res = await fetch('http://127.0.0.1:5000/get-lines', {
        method: 'POST',
        body: formData,
      });

      if (!res.ok) {
        throw new Error(`HTTP error! status: ${res.status}`);
      }

      const data = await res.json();
      console.log('Response data:', data);

      if (data.x1 !== undefined && data.y1 !== undefined) {
        drawLineOnCanvas(data.x1, data.y1, data.x2, data.y2);
      } else {
        setError('No vanishing point found.');
      }
    } catch (err) {
      setError(err.message);
    }
  };

  const drawLineOnCanvas = (x1, y1, x2, y2) => {
    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    const img = new Image();
    img.src = imageURL;
    img.onload = () => {
      canvas.width = img.width;
      canvas.height = img.height;
      ctx.drawImage(img, 0, 0);

      ctx.strokeStyle = 'red';
      ctx.lineWidth = 2;
      ctx.beginPath();
      ctx.moveTo(x1, y1);
      ctx.lineTo(x2, y2);
      ctx.stroke();
    };
  };

  return (
    <div style={{ padding: 20 }}>
      <h1>Vanishing Point Detection</h1>

      <div style={{ marginBottom: 10 }}>
        <input type="file" accept="image/*" onChange={handleFileChange} />
      </div>

      <button onClick={handleUpload}>
        Upload & Detect
      </button>

      {imageURL && <img src={imageURL} alt="Uploaded" style={{ marginTop: 20, maxWidth: '100%' }} />}
      <canvas ref={canvasRef} style={{ marginTop: 20 }} />

      {error && <p style={{ color: 'red' }}>{error}</p>}
    </div>
  );
}

export default App;