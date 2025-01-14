import firebase_admin
from firebase_admin import credentials, auth

# Path to your Firebase service account key JSON file
SERVICE_ACCOUNT_KEY = "config/firebase-admin-sdk.json"

# Initialize Firebase Admin SDK
cred = credentials.Certificate(SERVICE_ACCOUNT_KEY)