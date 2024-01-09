import os
import pickle
import cvzone
import numpy as np
import cv2
import face_recognition
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage
from datetime import datetime

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    "databaseURL": "https://facerecognitionattendanc-151ea-default-rtdb.firebaseio.com/",
    "storageBucket": "facerecognitionattendanc-151ea.appspot.com"
})

bucket = storage.bucket()

cap = cv2.VideoCapture(0)
cap.set(3, 640)
cap.set(4, 480)

imageBackground = cv2.imread("Resources/background.png")

# Importing the mode images into a list so that we can display and use it later
modePathList = os.listdir("Resources/Modes")
imageModeList = []
for path in modePathList:
    imageModeList.append(cv2.imread(os.path.join("Resources/Modes", path)))
# Import/Load the encoding file
file = open("EncodeFile.p", "rb")
encodeListKnownWithIDs = pickle.load(file)
file.close()
encodeListKnown, studentID = encodeListKnownWithIDs
# print(studentID)


modeType = 3
counter = 0
id = -1
imageStudent = []

while True:
    success, img = cap.read()

    imgSmall = cv2.resize(img, (0, 0), None, 0.25, 0.25)
    imgSmall = cv2.cvtColor(imgSmall, cv2.COLOR_BGR2RGB)

    faceCurrentFrame = face_recognition.face_locations(imgSmall)
    encodeCurrentFrame = face_recognition.face_encodings(imgSmall, faceCurrentFrame)

    imageBackground[162:162 + 480, 55:55 + 640] = img
    imageBackground[44:44 + 633, 808:808 + 414] = imageModeList[modeType]

    if faceCurrentFrame:

        for encodeFace, faceLocation in zip(encodeCurrentFrame, faceCurrentFrame):
            matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
            faceDistance = face_recognition.face_distance(encodeListKnown, encodeFace)
            # print("Matches: ", matches)
            # print("Face Distance: ", faceDistance)

            matchIndex = np.argmin(faceDistance)
            # print("Match Index:", matchIndex)

            if matches[matchIndex]:
                # print("Known Face Detected")
                # print(studentID[matchIndex])
                y1, x2, y2, x1 = faceLocation
                y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
                bbox = 55 + x1, 162 + y1, x2 - x1, y2 - y1
                cvzone.cornerRect(imageBackground, bbox, rt=0)
                id = studentID[matchIndex]

                if counter == 0:
                    cvzone.putTextRect(imageBackground, "Loading", (275, 400))
                    cv2.imshow("Face Attendance", imageBackground)
                    cv2.waitKey(1)
                    counter = 1
                    modeType = 1

        if counter != 0:

            if counter == 1:

                # Get the data
                studentInfo = db.reference(f'Students/{id}').get()
                print(studentInfo)

                # Get the image from the storage
                blob = bucket.get_blob(f'Images/{id}.png')
                array = np.frombuffer(blob.download_as_string(), np.uint8)
                imageStudent = cv2.imdecode(array, cv2.COLOR_BGRA2BGR)

                # Update data of attendance
                datetimeObject = datetime.strptime(studentInfo['last_attendance_time'], "%Y-%m-%d %H:%M:%S")
                secondsElapsed = (datetime.now() - datetimeObject).total_seconds()
                print(secondsElapsed)

                # This will only be 30 seconds. But in order to make it real-time, the 30 should be changed to the total number of seconds in a day
                if secondsElapsed > 30:
                    reference = db.reference(f'Students/{id}')
                    studentInfo['total_attendance'] += 1
                    reference.child('total_attendance').set(studentInfo['total_attendance'])
                    reference.child('last_attendance_time').set(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                else:
                    modeType = 0
                    counter = 0
                    imageBackground[44:44 + 633, 808:808 + 414] = imageModeList[modeType]

            if modeType != 0:
                if 10 < counter < 20:
                    modeType = 2

                imageBackground[44:44 + 633, 808:808 + 414] = imageModeList[modeType]

                if counter <= 10:
                    cv2.putText(imageBackground, str(studentInfo['total_attendance']), (861, 125), cv2.FONT_HERSHEY_COMPLEX, 1,
                                (255, 255, 255), 1)
                    cv2.putText(imageBackground, str(studentInfo['major']), (1006, 550), cv2.FONT_HERSHEY_COMPLEX, 0.5,
                                (255, 255, 255), 1)
                    cv2.putText(imageBackground, str(id), (1006, 493), cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255), 1)
                    cv2.putText(imageBackground, str(studentInfo['academic_standing']), (910, 625), cv2.FONT_HERSHEY_COMPLEX,
                                0.6, (100, 100, 100), 1)
                    cv2.putText(imageBackground, str(studentInfo['year']), (1025, 625), cv2.FONT_HERSHEY_COMPLEX, 0.6,
                                (100, 100, 100), 1)
                    cv2.putText(imageBackground, str(studentInfo['starting_year']), (1125, 625), cv2.FONT_HERSHEY_COMPLEX, 0.6,
                                (100, 100, 100), 1)

                    (w, h), _ = cv2.getTextSize(studentInfo['name'], cv2.FONT_HERSHEY_COMPLEX, 1, 1)
                    offsetOnWidth = (414 - w) // 2
                    cv2.putText(imageBackground, str(studentInfo['name']), (808 + offsetOnWidth, 445), cv2.FONT_HERSHEY_COMPLEX,
                                1, (50, 50, 50), 1)

                    imageBackground[175:175 + 216, 909:909 + 216] = imageStudent

                counter += 1

                if counter >= 20:
                    counter = 0
                    modeType = 3
                    studentInfo = []
                    imageStudent = []
                    imageBackground[44:44 + 633, 808:808 + 414] = imageModeList[modeType]

    else:
        modeType = 3
        counter = 0

    cv2.imshow("Webcam", img)
    cv2.imshow("Face Attendance", imageBackground)
    cv2.waitKey(1)
