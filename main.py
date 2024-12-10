import tkinter as tk
from tkinter import *
import cv2
import numpy as np
import os
import time
import mysql.connector
import datetime
from PIL import Image
from tkinter import messagebox
from tkinter.simpledialog import askstring

# Database connection
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",  
        database="attendance_db"
    )

def save_student_details(Id, name, email, Date, Time):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        query = "INSERT INTO student_details (id, name, email, date, time) VALUES (%s, %s, %s, %s, %s)"
        cursor.execute(query, (Id, name, email, Date, Time))
        conn.commit()
        cursor.close()
        conn.close()
    except mysql.connector.Error as err:
        label = Label(frame, text=f"Error: {err}", fg='white',bg='red')
        label.config(font=("Courier", 30))
        label.pack(pady= 10)

def save_attendance(Id, name, timestamp, subject):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        query = "INSERT INTO attendance (id, name, timestamp, subject) VALUES (%s, %s, %s, %s)"
        cursor.execute(query, (Id, name, timestamp, subject))
        conn.commit()
        cursor.close()
        conn.close()
    except mysql.connector.Error as err:
       label = Label(frame, text=f"Error: {err}", fg='white',bg='red')
       label.config(font=("Courier", 30))
       label.pack(pady= 10)

window = tk.Tk()  #Makes main window
window.wm_title("Attendance Management System using Face Recognition")
window.geometry('1920x1080')
window.config(background="light grey")

# Create a frame
frame = Frame(window, bg='light grey')
frame.place(relx=0.1, rely=0.1, relwidth=0.8, relheight=0.8)

def clear_entry(entry):
    entry.delete(0, tk.END)

# Create a label
label = Label(frame, text="Attendance Management System using Face Recognition", fg='white',bg='black')
label.config(font=("Courier", 30))
label.pack(pady= 10)

# Create a label
label = Label(frame, text="Enter your ID", bg='grey')
label.config(font=("Courier", 20))
label.pack()

# Create a text entry box
entry = Entry(frame)
entry.pack(pady=10)
# Create a clear button
clear_button = Button(frame, text="Clear", command=lambda: clear_entry(entry), bg="black", fg="white", font=("Courier", 15))
clear_button.pack(pady=10)

# Create a label
label = Label(frame, text="Enter your Name", bg='grey')
label.config(font=("Courier", 20))
label.pack()

# Create a text entry box
entry2 = Entry(frame)
entry2.pack(pady=10)
# Create a clear button
clear_button = Button(frame, text="Clear", command=lambda: clear_entry(entry2), bg="black", fg="white", font=("Courier", 15))
clear_button.pack(pady=10)

# Create a label
label = Label(frame, text="Enter your Email", bg='grey')
label.config(font=("Courier", 20))
label.pack()

# Create a text entry box
entry3 = Entry(frame)
entry3.pack(pady=10)
# Create a clear button
clear_button = Button(frame, text="Clear", command=lambda: clear_entry(entry3), bg="black", fg="white", font=("Courier", 15))

# Add a confirmation dialog when closing the window
def on_closing():
    if messagebox.askyesno("Exit", "Are you sure you want to exit?"):
        window.destroy()

# Bind the close protocol to the confirmation function
window.protocol("WM_DELETE_WINDOW", on_closing)

def manually_fill(attendance_records):
    global sb
    sb = Toplevel(window)
    sb.title("Enter Subject")
    sb.geometry('1280x720')
    sb.config(background="light grey")
    
    # Subject Entry Field
    Label(sb, text="Enter Subject:", bg="grey", fg='black', font=("Courier", 20)).pack(pady=10)
    sub_entry = Entry(sb, font=("Courier", 15), width=30)
    sub_entry.pack(pady=10)
    
    def submit_subject():
        subject = sub_entry.get()
        if subject == '':
            Label(sb, text="Please enter a subject!", bg="red", font=("Courier", 15)).pack()
        else:
            for record in attendance_records:
                save_attendance(record["ID"], record["Name"], record["Time"], subject)
            Label(frame, text="Attendance recorded successfully!", bg="green", font=("Courier", 15)).pack()
            sb.destroy()
    Button(sb, text="Submit", command=submit_subject, bg="blue", fg="white", font=("Courier", 15)).pack(pady=10)

# Check if password is already set
def is_password_set(student_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        query = "SELECT admin_password FROM student_details WHERE id = %s"
        cursor.execute(query, (student_id,))
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        return result[0] if result else None  # Return password if found
    except mysql.connector.Error as err:
        print(f"Error fetching password: {err}")
        return None

# Save password in the database
def set_password(student_id, password):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        query = "UPDATE student_details SET admin_password = %s WHERE id = %s"
        cursor.execute(query, (password, student_id))
        conn.commit()
        cursor.close()
        conn.close()
    except mysql.connector.Error as err:
        print(f"Error setting password: {err}")

# Capture Image
def take_img():
    # Get Inputs
    Id = entry.get()
    name = entry2.get()
    email = entry3.get()

    # Check if password is set
    stored_password = is_password_set(Id)
    
    if not stored_password:  # If password is not set, ask to set one
        password = askstring("Set Password", "Enter a password to set:", show='*')
        if password:
            set_password(Id, password)
            label = Label(frame, text="Password set successfully. Now you can capture an image.", bg='green')
            label.config(font=("Courier", 15))
            label.pack(pady=10)
            return  # End function after setting password
        else:
            label = Label(frame, text="Password cannot be empty.", bg='red')
            label.config(font=("Courier", 15))
            label.pack(pady=10)
            return

    # If password is already set, validate it
    entered_password = askstring("Password", "Enter your password to continue:", show='*')
    if entered_password != stored_password:
        label = Label(frame, text="Invalid password. Access denied!", bg='red')
        label.config(font=("Courier", 15))
        label.pack(pady=10)
        return

    # If password is correct, continue with the image capture logic
    label = Label(frame, text="Password validated. Access granted.", bg='green')
    label.config(font=("Courier", 15))
    label.pack(pady=10)

    # Input Validation
    if Id.isnumeric():
        try:
            # Initialize Camera and Cascade
            cam = cv2.VideoCapture(0)
            harcascadePath = "haarcascade_frontalface_default.xml"
            faceCascade = cv2.CascadeClassifier(harcascadePath)
            samp_num = 0  
            # Create Directory for Images if not exists
            save_path = "Images/Original Images"
            if not os.path.exists(save_path):
                os.makedirs(save_path)

            label = Label(frame, text="Camera initialized. Capturing images...", bg='Yellow')
            label.config(font=("Courier", 15))
            label.pack(pady=10)
            while True:
                ret, img = cam.read()
                if not ret:
                    label = Label(frame, text="Failed to access the camera.",bg="red")
                    label.config(font=("Courier", 15))
                    label.pack()
                    break

                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                faces = faceCascade.detectMultiScale(gray, 1.3, 5)

                for (x, y, w, h) in faces:
                    samp_num += 1
                    face_img = img[y:y+h, x:x+w] 
                    img_path = os.path.join(save_path, f"{name}_{Id}.jpg")
                    cv2.imwrite(img_path, face_img)

                    # Display on camera feed
                    cv2.rectangle(img, (x, y), (x+w, y+h), (255, 0, 0), 2)
                    cv2.imshow("Face Capture", img)

                if cv2.waitKey(5) & 0xFF == ord('q'):
                    break
                elif samp_num >= 1:  
                    label = Label(frame, text="Image captured. Enrollment complete.", bg='green')
                    label.config(font=("Courier", 15))
                    label.pack()
                    break
            cam.release()
            cv2.destroyAllWindows()

            ts = time.time()
            Date = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d')
            Time = datetime.datetime.fromtimestamp(ts).strftime('%H:%M:%S')
            save_student_details(Id, name, email, Date, Time)
            
        except Exception as e:
            label = Label(frame, text=f"Error during image capture: {e}", bg='red')
            label.config(font=("Courier", 15))
            label.pack(pady=10)
    else:
        label = Label(frame, text="Invalid inputs. Please check and try again.",bg='red')
        label.config(font=("Courier", 15))
        label.pack(pady=10)
        
# Attendance
def attendance():
    samp_num=0
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    recognizer.read('Images/TrainingData.yml')
    cascadePath = "haarcascade_frontalface_default.xml"
    faceCascade = cv2.CascadeClassifier(cascadePath)
    attendance_records = []
    cam = cv2.VideoCapture(0)

    def fetch_student_name(student_id):
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            query = "SELECT name FROM student_details WHERE id = %s"
            cursor.execute(query, (student_id,))
            result = cursor.fetchone()
            return result[0]
        except mysql.connector.Error as err:
            label = Label(frame, text=f"{err}",bg="red")
            label.config(font=("Courier", 15))
            label.pack(pady=10)
            return "Unknown"
        
    while True:
        ret, img = cam.read()
        if not ret:
                    label = Label(frame, text="Failed to access the camera.",bg="red")
                    label.config(font=("Courier", 15))
                    label.pack(pady=10)
                    break
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = faceCascade.detectMultiScale(gray, 1.3, 5)
        for (x, y, w, h) in faces:
            samp_num += 1
            Id, _ = recognizer.predict(gray[y:y+h, x:x+w])
            name = fetch_student_name(Id)
            timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            attendance_records.append({"ID": Id,"Name": name,"Time": timestamp})
            cv2.rectangle(img, (x, y), (x+w, y+h), (255, 0, 0), 2)
            cv2.putText(img, str(Id), (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        cv2.imshow('Attendance',img)
        if cv2.waitKey(5) & 0xFF == ord('q'):
                    break 
        elif samp_num >= 3:
            label=Label(frame,text="Image captured for Attendance.",bg='green')  
            label.config(font=("Courier", 15))
            label.pack(pady=10)
            break
    cam.release()
    cv2.destroyAllWindows()

    manually_fill(attendance_records)
def train_img():
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
    label = Label(frame, text="Training completed successfully!", bg='green')
    label.config(font=("Courier", 15))
    label.pack(pady=10)
    
Button(frame, text="Attendance", command=attendance, bg="blue", fg="white", font=("Courier", 15)).pack(pady=10)
Button(frame, text="Capture Image", command=take_img, bg="green", fg="white", font=("Courier", 15)).pack(pady=10)
Button(frame, text="Train", command=train_img, bg="dark orange", fg="white", font=("Courier", 15)).pack(pady=10)

window.mainloop()
