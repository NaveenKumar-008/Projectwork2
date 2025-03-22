from flask import Flask, render_template, request, jsonify, session, redirect, url_for,Response
import sqlite3
import re
import os
import dlib
import cv2
import numpy as np
import time
import smtplib
from email.mime.multipart import MIMEMultipart  
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
import smtplib
from email.utils import formataddr

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Needed for session management

DATABASE = "db1.db"

conn = sqlite3.connect(DATABASE)
cur = conn.cursor()
cur.execute("""
    CREATE TABLE IF NOT EXISTS register(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        usermail TEXT,
        password TEXT
    )
""")

cur.execute("""
            create table if not exists user_details(id integer primary key autoincrement,
            name text, bike text,phone text, email text,
            imagefile1 blob,imagefile2 blob,imagefile3 blob,imagefile4 blob,imagefile5 blob
            )
""")


conn.commit()
conn.close()

@app.route('/')
def index():
    
    return render_template('register.html')


@app.route('/back')
def back():
    return render_template('dashboard.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['name']
        print(username)
        usermail = request.form['email']
        print(usermail)
        password = request.form['password']
        print(password)

        # Validate username (only letters allowed)
        if not re.match("^[A-Za-z]+$", username):
            return render_template('register.html', error="Username must only contain letters")

        # Validate email (must be a Gmail address)
        if not re.match("^[a-zA-Z0-9]+[a-zA-Z0-9._%+-]*@gmail\.com$", usermail):
            return render_template('register.html', error="Email must be a valid Gmail address")

        # Check if the email already exists in the database
        conn = sqlite3.connect(DATABASE)
        cur = conn.cursor()
        cur.execute("SELECT * FROM register WHERE usermail = ?", (usermail,))
        data = cur.fetchone()

        if data:
            # If email exists, show an alert message
            return render_template('register.html', alert_message="Email already exists")

        # Add user to the database if everything is valid
        cur.execute("INSERT INTO register (username, usermail, password) VALUES (?, ?, ?)", (username, usermail, password))
        conn.commit()

        # Return success message after registration
        return render_template('register.html', alert_message="Registered successfully")
    
    return render_template('register.html')

a=[]

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        usermail = request.form['email']
        a.append(usermail)
        password = request.form['password']
        
        conn = sqlite3.connect(DATABASE)
        cur = conn.cursor()
        cur.execute("SELECT * FROM register WHERE usermail = ? AND password = ?", (usermail, password))
        data = cur.fetchone()
        if data:
            session['email'] = usermail
            return render_template("dashboard.html")
        else:
            return render_template("register.html",alert_message="Incorrect Email & Password")
    return render_template('register.html')

@app.route('/user_details', methods=["GET", "POST"])
def user_details():
    if request.method == "POST":
        name = request.form['name']
        bike = request.form['bike']
        phone = request.form['phone']
        email = request.form['email']
        imagefile1 = request.files['image1']
        blobdata1 = imagefile1.read()
        imagefile2 = request.files['image2']
        blobdata2 = imagefile2.read()
        imagefile3 = request.files['image3']
        blobdata3 = imagefile3.read()
        imagefile4 = request.files['image4']
        blobdata4 = imagefile4.read()
        imagefile5 = request.files['image5']
        blobdata5 = imagefile5.read()

        con = sqlite3.connect(DATABASE)
        cur = con.cursor()

        # Check if bike, email, or phone already exists
        cur.execute("SELECT * FROM user_details WHERE bike=? OR email=? OR phone=?", (bike, email, phone))
        existing_user = cur.fetchone()

        if existing_user:
            
            return render_template('dashboard.html', alert_message="Bike Number, Email, or Phone already exists!")

        # Insert new user details
        cur.execute("""
            INSERT INTO user_details(name, bike, email, phone, imagefile1, imagefile2, imagefile3, imagefile4, imagefile5)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (name, bike, email, phone, blobdata1, blobdata2, blobdata3, blobdata4, blobdata5))
        
        con.commit()

        # Retrieve images from database
        cur.execute("SELECT imagefile1, imagefile2, imagefile3, imagefile4, imagefile5 FROM user_details WHERE bike=?", (bike,))
        image_file_names = cur.fetchone()
        con.close()

        # Save images to a folder
        folder_path = os.path.join('image_folder', name)
        os.makedirs(folder_path, exist_ok=True)

        for i, image_file_data in enumerate(image_file_names):
            if image_file_data:
                image_path = os.path.join(folder_path, f'{name}_{i + 1}.jpg')
                with open(image_path, 'wb') as image_file:
                    image_file.write(image_file_data)

        
        return render_template('dashboard.html', alert_message="User details added successfully!")

    return render_template('dashboard.html')





@app.route('/track')
def track():
    return render_template('track.html')


detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")
face_recognizer = dlib.face_recognition_model_v1("dlib_face_recognition_resnet_model_v1.dat")

training_data_folder = 'image_folder'
face_encodings = []
labels = []

def send_email_alert(useremail):
    sender_email = '12a27naveenkumarm@gmail.com'
    sender_password = 'pohdbkfqmprowhcx'
    receiver_email = session['email']
    host = "smtp.gmail.com"
    mmail = "12a27naveenkumarm@gmail.com"        
    hmail = session['email']
    sender_name= "admin"
    receiver_name='user'
    msg = MIMEMultipart()
    subject = "Unknown Person Detected"
    text =f"Alert! An unknown person was detected by the system."
        ##             msg = MIMEText(text, 'plain')
    msg.attach(MIMEText(text, 'plain'))
    
    msg['To'] = formataddr((receiver_name, hmail))
    msg['From'] = formataddr((sender_name, mmail))
    msg['Subject'] = 'Respected sir/mam  ' 
    server = smtplib.SMTP(host, 587)
    server.ehlo()
    server.starttls()
                    
    server.login(mmail, sender_password)
    server.sendmail(mmail, [hmail], msg.as_string())
    server.quit()
    send="send"
    #print(send)

def load_face_encodings(data_folder):
    """Load known face encodings from the specified data folder."""
    face_encodings.clear()
    labels.clear()
    person_folder = os.path.join(training_data_folder, data_folder)

    if os.path.isdir(person_folder):
        for filename in os.listdir(person_folder):
            if filename.endswith(('.jpg', '.jpeg', '.png')):
                image_path = os.path.join(person_folder, filename)
                image = cv2.imread(image_path)
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                faces = detector(gray)

                for face in faces:
                    shape = predictor(gray, face)
                    face_encoding = np.array(face_recognizer.compute_face_descriptor(image, shape))
                    face_encodings.append(face_encoding)
                    labels.append(data_folder)  # Store the person's label

    #print(f"Loaded {len(face_encodings)} face encodings for {len(set(labels))} persons.")
    
@app.route('/video')
def run_face_recognition():
    """Run face recognition in the backend and display the camera feed locally (not in frontend)."""
    global data
    useremail = a[-1]  # Replace with actual email
    #print("User Email:", useremail)

    # Fetch associated folder for user's registered face data
    con = sqlite3.connect(DATABASE)  # Update with correct database path
    cur = con.cursor()
    cur.execute("SELECT name FROM user_details WHERE email=?", (useremail,))
    email = cur.fetchone()
    con.close()

    if email:
        data = email[0]
        #print("Loading face encodings for:", data)
        load_face_encodings(data)
    else:
        data = None

    cap = cv2.VideoCapture(0)  # Open camera

    # Ensure the camera initializes properly
    if not cap.isOpened():
        #print("Error: Camera not found or not accessible.")
        return

    time.sleep(2)  # Allow camera to warm up

    while True:
        ret, frame = cap.read()
        if not ret:
            #print("Error: Frame capture failed.")
            break  # Exit loop if camera fails

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = detector(gray, 1)  # Detect faces with an upsample factor

        unknown_detected = False  # Flag to prevent continuous unknown alerts

        if len(faces) > 0:
            #print(f"{len(faces)} Face(s) detected.")

            for face in faces:
                shape = predictor(gray, face)
                face_encoding = np.array(face_recognizer.compute_face_descriptor(frame, shape))

                if face_encodings:  # Ensure face_encodings is not empty before comparison
                    distances = np.linalg.norm(np.array(face_encodings) - face_encoding, axis=1)
                    min_distance_idx = np.argmin(distances)
                    min_distance = distances[min_distance_idx]

                    if min_distance < 0.5:  # Known person threshold
                        label = labels[min_distance_idx]
                        print(f"Recognized: {label} (Distance: {min_distance:.2f})")
                        imagefolder = f"new/{label}.jpg"
                        cv2.imwrite(imagefolder, frame)
                    else:
                        label = "Unknown"
                        print("Unknown face detected.")
                        if not unknown_detected:
                            send_email_alert(useremail)  # Send alert only once per unknown detection
                            unknown_detected = True

                # Draw rectangle around detected face
                x, y, w, h = face.left(), face.top(), face.width(), face.height()
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv2.putText(frame, label, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

        else:
            print("No face detected.")  # Keep detecting even if no face is found

        # ✅ Display camera feed only in the backend
        cv2.imshow("Face Recognition - Backend", frame)

        # Exit when 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    return render_template("track.html")

if __name__ == '__main__':
    app.run(port=500)
