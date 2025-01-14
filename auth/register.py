from firebase_admin import auth
from firebase_admin.exceptions import FirebaseError

def signup(email, password):
    try:
        user = auth.create_user(email=email, password=password)
        print("Registration successful!")
        return user
    except FirebaseError as e:
        error_message = str(e)
        if "EMAIL_EXISTS" in error_message:
            return "EMAIL_EXITS"
        elif "INVALID_EMAIL" in error_message:
            return "INVALID_EMAIL"
        elif "WEAK_PASSWORD" in error_message:
            return "WEAK_PASSWORD"
        else:
            print(f"Error registering user: {error_message}")
    except Exception as e:
        print(f"Unexpected error: {e}")
    return None