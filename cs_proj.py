# detect.py
import RPi.GPIO as GPIO
import time
import pigpio
import cv2, sys, numpy, os
from numpy import interp
import argparse

size = 4
fn_haar = 'haarcascade_frontalface_default.xml'
fn_name = "face"
pause=0
panServo = 2
tiltServo = 3 #not used
panPos = 1250
minMov = 20
maxMov = 50
tiltPos = 2300



servo = pigpio.pi()
servo.set_servo_pulsewidth(panServo, panPos)
servo.set_servo_pulsewidth(tiltServo, tiltPos)
(im_width, im_height) = (112, 92)
haar_cascade = cv2.CascadeClassifier(fn_haar)
webcam = cv2.VideoCapture(0)



while True:

    # Loop until the camera is working
    rval = False
    while(not rval):
        # Put the image from the webcam into 'frame'
        (rval, frame) = webcam.read()
        if(not rval):
            print("Failed to open webcam. Trying again...")

    # Get image size
    height, width, channels = frame.shape

    # Flip frame
    frame = cv2.flip(frame, 1, 0)

    # Convert to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Scale down for speed
    mini = cv2.resize(gray, (int(gray.shape[1] / size), int(gray.shape[0] / size)))

    # Detect faces
    faces = haar_cascade.detectMultiScale(mini)

    # consider largest face
    faces = sorted(faces, key=lambda x: x[1])
    if faces:
        face_i = faces[0]
        (x, y, w, h) = [v * size for v in face_i]
        print("x= "+ str(x)) #to debug
        print("y= "+ str(y))
        print("w= "+ str(w))
        print("h= "+ str(h))
        if int(x+(w/2)) > 360:
            panPos = int(panPos + interp(int(x+(w/2)), (360, 640), (minMov, maxMov)))
            
        elif int(x+(w/2)) < 280:
            
            panPos = int(panPos - interp(int(x+(w/2)), (280, 0), (minMov, maxMov)))
    
        
    
        if not panPos > 2500 or not panPos < 500:
            servo.set_servo_pulsewidth(panServo, panPos)
    
        

        face = gray[y:y + h, x:x + w]
        face_resize = cv2.resize(face, (im_width, im_height))

        # Draw rectangle and write name
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 10)
        cv2.putText(frame, fn_name, (x - 10, y - 10), cv2.FONT_HERSHEY_PLAIN,
            1,(0, 255, 0))

        # Remove false positives
        if(w * 6 < width or h * 6 < height):
            print("Face too small")
        else:
            if(pause == 0):

                print("face found ")
              #  print(gray)
    cv2.imshow('Detect Face', frame)
    key = cv2.waitKey(10)
    if key == ord('a'):
        cv2.destroyAllWindows()
        break
GPIO.cleanup()    
    
