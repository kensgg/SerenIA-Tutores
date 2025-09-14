import os
import json
import firebase_admin
from firebase_admin import credentials, firestore

def initialize_firebase():
    """
    Initializes Firebase and returns the Firestore client.
    
    Returns:
        firestore.Client: The Firestore client instance.
    """
    current_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(current_dir, '..', 'config', 'firebase_config.json')

    try:
        with open(config_path, 'r') as f:
            config = json.load(f)

        if not firebase_admin._apps:
            cred = credentials.Certificate(config)
            firebase_admin.initialize_app(cred)
            print("Firebase initialized successfully!")
        
        db = firestore.client()
        return db
    except Exception as e:
        print(f"Error initializing Firebase: {e}")
        raise

db = initialize_firebase()

__all__ = ['initialize_firebase', 'db']