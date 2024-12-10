import cv2
import numpy as np

recognizer=cv2.face.LBPHFaceRecognizer_create()
recognizer.read('Images/TrainingData.yml')
cascadePath = "haarcascade_frontalface_default.xml"
faceCascade = cv2.CascadeClassifier(cascadePath)
font=cv2.FONT_HERSHEY_SIMPLEX

cam=cv2.VideoCapture(0)
while True:
    ret, im = cam.read()
    gray=cv2.cvtColor(im,cv2.COLOR_BGR2GRAY)
    faces=faceCascade.detectMultiScale(gray, scaleFactor=1.2, minNeighbors=5)# scaleFactor compensates for faces appearing smaller as they are further away from the camera
    for(x,y,w,h) in faces:
        
        Id=recognizer.predict(gray[y:y+h,x:x+w]) 
        cv2.rectangle(im,(x,y),(x+w,y+h),(225,0,0),2) #drawing rectangle around the face
        cv2.putText(im,str(Id[0]), (x,y+h),font, 1, (255,255,255),2)#putting the name of the person on the face
    cv2.imshow('im',im)
    if cv2.waitKey(10) & 0xFF==ord('q'):
        break
cam.release()
cv2.destroyAllWindows()