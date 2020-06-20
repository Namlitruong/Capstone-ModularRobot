import cv2
import time
import numpy as np


cap = cv2.VideoCapture(1); #variable to save livestream from camera

while (cap.isOpened() ):
    ret, frame = cap.read() #if the frame is available ret will become true
    # The frame (image/video) will be saved to 'frame'

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)


 #   cv2.imshow('frame', frame) # show the frame in a window

    blackline = cv2.inRange(frame, (0,0,0), (60,60,60)) #detect black (0-50) in the picture

    kernel = np.ones ((3,3), np.uint8)

    blackline = cv2.erode(blackline, kernel, iterations= 15)
    blackline = cv2.dilate(blackline,kernel, iterations= 20)
    #get contours data from the blackline picture
    contours, hierarchy = cv2.findContours(blackline.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    cv2.drawContours(frame,contours,-1,(255,0,0),3) # draw the contours on the ORIGINAL IMAGE


    if len(contours) >0:
        x,y,w,h = cv2.boundingRect(contours[0])
        cv2.rectangle(frame, (x,y),(x+w,y+h), (0,0,255), 3)
        cv2.line(frame, (x+(w//2),0), (x+(w//2),480), (0,255,0),3)

    cv2.imshow('black', blackline)
    cv2.imshow('blackline with contours ', frame )
    cv2.imshow('black2', blackline)
    if cv2.waitKey(1) & 0xFF == ord('q'): #wait for 'q' key to break from the while loop
        break

cap.release()
cv2.destroyAllWindows()