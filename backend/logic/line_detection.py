import cv2
import numpy as np
import math

# Global variables
selected_lines = []
rotating = False
vanishing_calculated = False
vanishing_line = None

def api_test():
    return {"lines": ["line1", "line2", "line3"]}

def detect_and_draw_lines(img):
    edges = cv2.Canny(img, 100, 450)
    cv2.imshow("Edges", edges)
    lines = cv2.HoughLinesP(
        edges,
        rho=1,
        theta=np.pi/180,
        threshold=150,
        minLineLength=250,
        maxLineGap=100
    )
    
    output = img.copy()
    line_list = []
    slope_list = []

    if lines is not None:
        for l in lines:
            x1, y1, x2, y2 = l[0]
            dx = x2 - x1
            dy = y2 - y1
            if dx == 0 or dy == 0:
                continue
            line_list.append([x1, y1, x2, y2])
            slope_list.append(dy/dx)
            extend_line(output, x1, y1, x2, y2, (0, 0, 255))

    return output, line_list

def extend_line(img, x1, y1, x2, y2, color):
    height, width = img.shape[:2]
    if x2 != x1:
        slope = (y2 - y1) / (x2 - x1)
        intercept = y1 - slope * x1
        y_start = int(slope * 0 + intercept)
        y_end = int(slope * width + intercept)
        cv2.line(img, (0, y_start), (width, y_end), color, 2)
    else:
        cv2.line(img, (x1, 0), (x1, height), color, 2)

def calculate_vanishing_point(line1, line2):
    x1, y1, x2, y2 = line1
    x3, y3, x4, y4 = line2

    # Calculate slopes and intercepts
    m1 = (y2 - y1) / (x2 - x1)
    c1 = y1 - m1 * x1
    m2 = (y4 - y3) / (x4 - x3)
    c2 = y3 - m2 * x3

    # Calculate intersection
    if m1 != m2:
        x_vanish = (c2 - c1) / (m1 - m2)
        y_vanish = m1 * x_vanish + c1
        return int(x_vanish), int(y_vanish)
    return None

def mouse_callback(event, x, y, flags, param):
    global selected_lines, rotating, vanishing_calculated, vanishing_line

    if event == cv2.EVENT_LBUTTONDOWN:
        if vanishing_line:
            x1, y1 = vanishing_line[0]
            x2, y2 = vanishing_line[1]
            if abs((y - y1) - ((y2 - y1) / (x2 - x1)) * (x - x1)) < 10:
                rotating = True
        else:
            for i, (x1, y1, x2, y2) in enumerate(param):
                if abs(x - x1) < 10 and abs(y - y1) < 10:
                    if i not in selected_lines:
                        selected_lines.append(i)
                    if len(selected_lines) > 2:
                        selected_lines.pop(0)
                    vanishing_calculated = False
                    vanishing_line = None
                    break

    elif event == cv2.EVENT_MOUSEMOVE and rotating:
        x1, y1 = vanishing_line[0]
        length = math.sqrt((x - x1) ** 2 + (y - y1) ** 2)
        angle = math.atan2(y - y1, x - x1)
        x2 = int(x1 + length * math.cos(angle))
        y2 = int(y1 + length * math.sin(angle))
        vanishing_line = ((x1, y1), (x2, y2))

    elif event == cv2.EVENT_LBUTTONUP:
        rotating = False

if __name__ == "__main__":
    img = cv2.imread("offside.png")
    if img is not None:
        result, lines = detect_and_draw_lines(img)
        cv2.namedWindow("Vanishing Point")
        cv2.setMouseCallback("Vanishing Point", mouse_callback, lines)

        while True:
            temp_img = img.copy()
            for i, (x1, y1, x2, y2) in enumerate(lines):
                color = (0, 255, 0) if i in selected_lines else (0, 0, 255)
                extend_line(temp_img, x1, y1, x2, y2, color)

            if len(selected_lines) == 2 and not vanishing_calculated:
                line1 = lines[selected_lines[0]]
                line2 = lines[selected_lines[1]]
                vanishing_point = calculate_vanishing_point(line1, line2)
                if vanishing_point:
                    x_vanish, y_vanish = vanishing_point
                    slope1 = (line1[3] - line1[1]) / (line1[2] - line1[0])
                    slope2 = (line2[3] - line2[1]) / (line2[2] - line2[0])
                    avg_slope = (slope1 + slope2) / 2
                    intercept = y_vanish - avg_slope * x_vanish
                    y_start = int(avg_slope * 0 + intercept)
                    y_end = int(avg_slope * temp_img.shape[1] + intercept)
                    vanishing_line = ((x_vanish, y_vanish), (temp_img.shape[1], y_end))
                    vanishing_calculated = True

            if vanishing_line:
                cv2.line(temp_img, vanishing_line[0], vanishing_line[1], (0, 255, 255), 2)

            cv2.imshow("Vanishing Point", temp_img)
            
            if cv2.waitKey(1) & 0xFF == 27:  # Press 'Esc' to exit
                break

        cv2.destroyAllWindows()
