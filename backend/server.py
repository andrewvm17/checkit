# app.py
import io
import cv2
import numpy as np
from PIL import Image
from flask import Flask, request, jsonify
from logic.detector_v2 import detect_lines_with_new_algorithm
from flask_cors import CORS


app = Flask(__name__)
CORS(app)

@app.route('/get-lines', methods=['POST'])
def get_lines():
    # 1. Get the file from the POST request
    file = request.files.get('image')
    if not file:
        return jsonify({"error": "No file uploaded"}), 400

    # 2. Convert the file to a NumPy array for OpenCV
    in_memory_file = io.BytesIO(file.read())
    pil_img = Image.open(in_memory_file).convert("RGB")
    cv_img = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)

    # 3. Detect lines
    line = detect_lines_with_new_algorithm(cv_img)
    
    if line:
        # Convert the line tuple to a JSON-serializable format
        x1 = int(line[0][0])
        y1 = int(line[0][1])
        x2 = int(line[1][0])
        y2 = int(line[1][1])
        slope = float(line[2])

        return jsonify({
            "x1": x1,
            "y1": y1,
            "x2": x2,
            "y2": y2,
            "slope": slope
        })

    else:
        return jsonify({"line": None})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
