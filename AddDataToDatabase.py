import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    "databaseURL": "https://facerecognitionattendanc-151ea-default-rtdb.firebaseio.com/"
})

reference = db.reference("Students")

data = {
    "123456":
        {
            "name": "Connor McGregor",
            "major": "Kinesiology",
            "starting_year": 1999,
            "total_attendance": 20,
            "academic_standing": "Good",
            "year": 4,
            "last_attendance_time": "2023-12-23 00:54:34"
        },
    "567890":
        {
            "name": "Madison Beer",
            "major": "Cosmetics",
            "starting_year": 2004,
            "total_attendance": 28,
            "academic_standing": "Good",
            "year": 8,
            "last_attendance_time": "2023-12-23 00:54:34"
        },
    "654321":
        {
            "name": "Tom Holland",
            "major": "Acting",
            "starting_year": 2006,
            "total_attendance": 40,
            "academic_standing": "Bad",
            "year": 4,
            "last_attendance_time": "2023-12-23 00:54:34"
        }
}

for key, value in data.items():
    reference.child(key).set(value)
