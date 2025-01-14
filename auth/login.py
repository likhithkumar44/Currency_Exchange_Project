import requests
from dotenv import load_dotenv
import os


def login(email, password):
    load_dotenv()
    FIREBASE_API = os.getenv("FIREBASE_API")
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={FIREBASE_API}"
    payload = {
        "email": email,
        "password": password,
        "returnSecureToken": True,
    }
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        data = response.json()
        print("Login successful!")
        return data
    
    except requests.exceptions.HTTPError as e:
        error_response = response.json()
        if "error" in error_response:
            error_code = error_response["error"]["message"]
            return error_code
        else:
            print("An unknown error occurred.")
        return None
    
    except requests.exceptions.RequestException as e:
        print(f"Error logging in: {e}")
        return None