import cv2
import numpy as np
import time
import imutils
from collections import deque


cap = cv2.VideoCapture(0)

_, frame = cap.read()
rows, cols, _ = frame.shape

x_medium = int(cols / 2)
y_medium = int(rows / 2)
center = int(cols / 2)
position = 90 # degrees

def nothing(x):
    pass

cv2.namedWindow("Control")
cv2.createTrackbar("LH", "Control", 150, 255, nothing)
cv2.createTrackbar("LS", "Control", 155, 255, nothing)
cv2.createTrackbar("LV", "Control", 85, 255, nothing)
cv2.createTrackbar("HH", "Control", 180, 255, nothing)
cv2.createTrackbar("HS", "Control", 255, 255, nothing)
cv2.createTrackbar("HV", "Control", 255, 255, nothing)

while True:
    _, frame = cap.read()
    blur = cv2.GaussianBlur(frame, (11, 11), 0)
    hsv = cv2.cvtColor(blur, cv2.COLOR_BGR2HSV)
    #hsv = cv2.flip(hsv, 1);
    
    low_h = cv2.getTrackbarPos("LH", "Control")
    low_s = cv2.getTrackbarPos("LS", "Control")
    low_v = cv2.getTrackbarPos("LV", "Control")
    high_h = cv2.getTrackbarPos("HH", "Control")
    high_s = cv2.getTrackbarPos("HS", "Control")
    high_v = cv2.getTrackbarPos("HV", "Control")
    
    
    low_red = np.array([low_h, low_s, low_v])
    high_red = np.array([high_h, high_s, high_v])
    mask = cv2.inRange(hsv, low_red, high_red)
    mask = cv2.erode(mask, None, iterations=2)
    mask = cv2.dilate(mask, None, iterations=2)
    res = cv2.bitwise_and(frame, frame, mask=mask)
    contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    contours = sorted(contours, key=lambda x:cv2.contourArea(x), reverse=True)
    
    
    for cnt in contours:
        (x, y, w, h) = cv2.boundingRect(cnt)
        
        x_medium = int((x + x + w) / 2)
        break 
    for cnt in contours:
        (x, y, w, h) = cv2.boundingRect(cnt)
        
        y_medium = int((y + y + h) / 2)
        break
    
    cv2.line(frame, (x_medium, 0), (x_medium, 480), (0, 255, 0), 2)
    cv2.line(frame, (0, y_medium), (640, y_medium), (0, 255, 0), 2)
    cv2.line(mask, (x_medium, 0), (x_medium, 480), (0, 255, 0), 1)
    cv2.line(mask, (0, y_medium), (640, y_medium), (0, 0, 255), 1)
    
    
    cv2.imshow("Frame", frame)

    cv2.imshow("Mask", mask)
    cv2.imshow("Res", res)
    key = cv2.waitKey(1)
    
    

    
    if key == 27:   # esc key
        break
        
cap.release()
cv2.destroyAllWindows()