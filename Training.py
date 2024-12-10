import cv2
import os
import numpy as np
from PIL import Image

recogniser=cv2.face.LBPHFaceRecognizer_create() #Local Binary Pattern Histogram Face Recognizer
detector=cv2.CascadeClassifier("haarcascade_frontalface_default.xml") #Cascade Classifier for face detection in an image or video stream 

def getImageAndLabels(path):
    # path is the path to the directory containing the images
    imagePaths=[os.path.join(path,f) for f in os.listdir(path)] # creating a list of image paths in the directory
    #creating list of faces and ids
    faceSamples=[]
    ids=[]
    for imagePath in imagePaths:
        PIL_img=Image.open(imagePath).convert('L') #converts the image to grayscale
        img_numpy=np.array(PIL_img,'uint8') #converts the image to numpy array
        id=int(os.path.split(imagePath)[-1].split("_")[1].split(".")[0]) # extracting the id from the image name of the form name_id.jpg
        faces=detector.detectMultiScale(img_numpy) #detects faces in the image
        for (x,y,w,h) in faces:
            faceSamples.append(img_numpy[y:y+h,x:x+w]) #appending the face to the faceSamples list
            ids.append(id) 
    return faceSamples,ids

faces,ids= getImageAndLabels('Images/Original Images')
recogniser.train(faces,np.array(ids))
recogniser.write('Images/TrainingData.yml')
cv2.destroyAllWindows()
