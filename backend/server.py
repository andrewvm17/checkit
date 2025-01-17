# app.py
import io
import cv2
import numpy as np
from PIL import Image
from flask import Flask, request, jsonify
from line_detection import api_test

app = Flask(__name__)

@app.route('/detect-vanishing', methods=['POST'])
def detect_vanishing():
    # 1. Get the file from the POST request
    file = request.files.get('image')
    if not file:
        return jsonify({"error": "No file uploaded"}), 400

    # 2. Convert the file to a NumPy array for OpenCV
    in_memory_file = io.BytesIO(file.read())
    pil_img = Image.open(in_memory_file).convert("RGB")
    cv_img = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)

    # 3. Calculate vanishing point
    vp = get_vanishing_point(cv_img)

    if vp:
        x_vanish, y_vanish = vp
        return jsonify({"vanishing_point": [x_vanish, y_vanish]})
    else:
        return jsonify({"vanishing_point": None})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
