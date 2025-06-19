import firebase_admin
from firebase_admin import credentials, firestore, storage

# Load service account key
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    'storageBucket':'machine-data-form.appspot.com'
})

db = firestore.client()
bucket = storage.bucket()
