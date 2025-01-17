#!/usr/bin/env python3
import sys
import cv2
import numpy as np
import io
from PIL import Image

def detect_white_lines(image):
    """
    Convert the image (BGR) to HLS, then apply a range filter
    to isolate white-ish areas.
    """
    # Convert BGR to HLS
    hls = cv2.cvtColor(image, cv2.COLOR_BGR2HLS)

    # Define lower and upper thresholds for 'white' in HLS
    # Adjust based on your specific pitch/lighting conditions
    lower_white = np.array([0, 180, 0])      # hue=0, lightness=180, saturation=0
    upper_white = np.array([255, 255, 100])  # hue=255, lightness=255, saturation=100

    # Create a binary mask where white-ish regions are 255
    mask = cv2.inRange(hls, lower_white, upper_white)
    return mask

def clean_mask(mask):
    """
    Apply morphological operations to remove noise and close small holes.
    Adjust the kernel size depending on how thick/continuous your lines are.
    """
    kernel = np.ones((5, 5), np.uint8)
    closed_mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    return closed_mask

def highlight_contours(img, mask):
    """
    Find white-line contours and draw them in red.
    This approach treats lines as thicker regions.
    """
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area > 500:  # filter out small noise
            cv2.drawContours(img, [cnt], -1, (0, 0, 255), 3)
    return img

def hough_line_detection(img, mask):
    """
    Use a Hough transform to detect line segments.
    Draw the resulting lines in red.
    """
    edges = cv2.Canny(mask, 50, 150)
    lines = cv2.HoughLinesP(
        edges, 
        rho=1, 
        theta=np.pi/180, 
        threshold=100, 
        minLineLength=50, 
        maxLineGap=20
    )
    
    if lines is not None:
        for line in lines:
            x1, y1, x2, y2 = line[0]
            cv2.line(img, (x1, y1), (x2, y2), (0, 0, 255), 3)
    return img

def main():
    if len(sys.argv) < 2:
        print("Usage: python line_detector_v1.py <image_path>")
        sys.exit(1)

    image_path = sys.argv[1]

    # Read the image from disk
    image = cv2.imread(image_path)
    if image is None:
        print(f"Error: Could not open or find the image '{image_path}'.")
        sys.exit(1)

    # Detect "white" lines in the image
    mask = detect_white_lines(image)

    # Clean up the mask with morphological operations
    cleaned_mask = clean_mask(mask)

    # --- CHOOSE YOUR DETECTION METHOD ---

    # 1) Contour detection
    #highlighted = highlight_contours(image.copy(), cleaned_mask)

    # 2) Hough transform (active by default here)
    highlighted = hough_line_detection(image.copy(), cleaned_mask)

    # Show results
    cv2.imshow("Original", image)
    cv2.imshow("Mask (Initial)", mask)
    cv2.imshow("Mask (Cleaned)", cleaned_mask)
    cv2.imshow("Highlighted Lines", highlighted)

    print("Press any key on the image window to exit.")
    cv2.waitKey(0)
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
