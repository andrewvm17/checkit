// App.js
import React, { useState } from 'react';

function App() {
  const [selectedFile, setSelectedFile] = useState(null);
  const [vanishingPoint, setVanishingPoint] = useState(null);
  const [error, setError] = useState('');

  const handleFileChange = (e) => {
    setSelectedFile(e.target.files[0]);
  };

  const handleUpload = async () => {
    if (!selectedFile) {
      setError('No file selected');
      return;
    }

    try {
      // Prepare form data
      const formData = new FormData();
      formData.append('image', selectedFile);

      // Send the request
      const res = await fetch('http://127.0.0.1:5000/detect-vanishing', {
        method: 'POST',
        body: formData,
      });

      if (!res.ok) {
        throw new Error(`HTTP error! status: ${res.status}`);
      }

      const data = await res.json();
      // data will be something like: { vanishing_point: [x, y] } or null

      if (data.vanishing_point) {
        setVanishingPoint(data.vanishing_point);
      } else {
        setVanishingPoint(null);
        setError('No vanishing point found.');
      }
    } catch (err) {
      setVanishingPoint(null);
      setError(err.message);
    }
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

      {vanishingPoint && (
        <p>Vanishing Point: ({vanishingPoint[0]}, {vanishingPoint[1]})</p>
      )}
      {error && <p style={{ color: 'red' }}>{error}</p>}
    </div>
  );
}

export default App;
