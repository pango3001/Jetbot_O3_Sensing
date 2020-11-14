import cv2
import numpy as np
import time
import Adafruit_PCA9685

#servo driver board
pwm = Adafruit_PCA9685.PCA9685()

#servo stuff
pwm.set_pwm_freq(60)
servo_min = 150  # Min pulse length out of 4096
servo_max = 600  # Max pulse length out of 4096

#raspi camera
cap = cv2.VideoCapture(0)

#set capture resolution (smaller for sake of speed)
cap.set(3,480)
cap.set(4,320)
_, frame = cap.read()
rows, cols, _ = frame.shape

x_medium = int(cols / 2)
y_medium = int(rows / 2)
x_center = int(cols / 2)
y_center = int(rows / 2)
x_position = int((600-150)/2) # starting x position 150 low     600 high
y_position = int(480) # starting y position 150 low     600 high
buffer = 50 #pixels

#center servos
pwm.set_pwm(0, 0, x_position)
pwm.set_pwm(2, 0, y_position)



def nothing(x):
    pass

def x_posit(x):
    global x_position
    x_position += x
    if x_position > servo_max:
        x_position = servo_max
    if x_position < servo_min:
        x_position = servo_min
    pwm.set_pwm(0, 0, x_position)

def y_posit(x):
    global y_position
    y_position += x
    if y_position > servo_max:
        y_position = servo_max
    if y_position < servo_min:
        y_position = servo_min
    pwm.set_pwm(2, 0, y_position)


#HSV Control Window   initially set to track red
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
    
    # tracking
    for cnt in contours:
        (x, y, w, h) = cv2.boundingRect(cnt)
        x_medium = int((x + x + w) / 2)
        break 
    for cnt in contours:
        (x, y, w, h) = cv2.boundingRect(cnt)
        y_medium = int((y + y + h) / 2)
        break
    
    #move x axis servo
    if x_medium < x_center - buffer:
        x_posit(3)
    elif x_medium > x_center + buffer:
        x_posit(-3)
        
    #move y axis servo    
    if y_medium < y_center - buffer:
        y_posit(-3)
    elif y_medium > y_center + buffer:
        y_posit(3)
        
        
    
    #buffer lines
    cv2.line(frame, (x_center - buffer,0), (x_center - buffer, 480), (0, 255, 255), 2)
    cv2.line(frame, (x_center + buffer,0), (x_center + buffer, 480), (0, 255, 255), 2)
    cv2.line(frame, (0, y_center - buffer), (640, y_center - buffer), (0, 255, 255), 2)
    cv2.line(frame, (0, y_center + buffer), (640, y_center + buffer), (0, 255, 255), 2)
    
    
    #tracking ling
    cv2.line(frame, (x_medium, 0), (x_medium, 480), (0, 255, 0), 2)
    cv2.line(frame, (0, y_medium), (640, y_medium), (0, 255, 0), 2)
    cv2.line(mask, (x_medium, 0), (x_medium, 480), (0, 255, 0), 1)
    cv2.line(mask, (0, y_medium), (640, y_medium), (0, 0, 255), 1)
    
    #GUI Windows of video feed
    cv2.imshow("Frame", frame)
    cv2.imshow("Mask", mask)
    #cv2.imshow("Res", res)
    key = cv2.waitKey(1)
    
    if key == 27:   # esc key
        break
        
cap.release()
cv2.destroyAllWindows()