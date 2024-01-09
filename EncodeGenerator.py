import cv2
import face_recognition
import pickle
import os
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    "databaseURL": "https://facerecognitionattendanc-151ea-default-rtdb.firebaseio.com/",
    "storageBucket": "facerecognitionattendanc-151ea.appspot.com"
})

# Importing the student images
folderPath = "Images"
imagePathList = os.listdir(folderPath)
imageList = []
studentID = []
for path in imagePathList:
    imageList.append(cv2.imread(os.path.join(folderPath, path)))
    studentID.append(os.path.splitext(path)[0])

    fileName = f"{folderPath}/{path}"
    bucket = storage.bucket()
    blob = bucket.blob(fileName)
    blob.upload_from_filename(fileName)


# The 'os.path.splitext(path)' splits the ID number and png from each other. Then we have to get the first element which is the
# ID number alone. The reason we are not getting just the first six numbers is because the ID number can vary in terms of how
# many numbers are in it.
def findEncodings(imagesList):
    encodeList = []
    for image in imagesList:
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        encode = face_recognition.face_encodings(image)[0]
        encodeList.append(encode)

    return encodeList


print("Encoding started .....")
encodeListKnown = findEncodings(imageList)
encodeListKnownWithIDs = [encodeListKnown, studentID]
print("Encoding complete")

# Now we must create the pickle file, so we can export it
file = open("EncodeFile.p", "wb")
pickle.dump(encodeListKnownWithIDs, file)
file.close()
print("File Saved")
