from google.cloud import storage
from google.oauth2 import service_account
import uuid
import requests

# GCP setup
SERVICE_ACCOUNT_FILE = './dependencies/dsci551-416302-9c06656dc6b8.json'
BUCKET_NAME = 'dsci551-project'

# Global API endpoint
API_BASE_URL = 'http://127.0.0.1:5001' # Choose this if running locally

# API_BASE_URL = 'https://dsci551-server-production.up.railway.app'

# Authenticate using service account
credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE)
client = storage.Client(credentials=credentials, project=credentials.project_id)

def create_uuid():
    # Generate a random UUID
    file_uuid = uuid.uuid4()
    # Convert UUID to a string and remove hyphens to get 32 characters
    file_uuid_32 = str(file_uuid).replace('-', '')
    return file_uuid_32

def upload_file_to_gcs(file):
    bucket = client.bucket(BUCKET_NAME)
    blob = bucket.blob(create_uuid() + ".wav")
    blob.upload_from_string(file.getvalue(), content_type=file.type)

    return blob.public_url

def send_to_api(track_info):
    # API endpoint URL
    api_endpoint = f'{API_BASE_URL}/api/audio/upload'
    
    # Adjust the JSON payload to match the API's expected format
    json_data = {
        "artistName": track_info['artist_name'],
        "trackName": track_info['track_name'],
        "fileUrl": track_info['file_url']
    }
    
    # Headers to indicate that the request body is JSON
    headers = {'Content-Type': 'application/json'}
    
    # Send a POST request with the JSON payload
    response = requests.post(api_endpoint, json=json_data, headers=headers)
    
    # Assuming the response's content type is JSON, parse and return the response JSON
    return response.json()

def fetch_audio_files(page=1, sort_by='created_at', order='desc', limit=10):
    # Build the API endpoint URL with sorting parameters
    api_endpoint = f'{API_BASE_URL}/api/audio/list?page={page}&sort_by={sort_by}&order={order}&limit={limit}'
    response = requests.get(api_endpoint)
    if response.status_code == 200:
        return response.json()  # Returns the parsed JSON response
    else:
        return None  # In case of a non-successful status code

def search_audio_files(artist_name='', track_name=''):
    if not artist_name and not track_name:
        print('Please provide an artist name or a track name to search.')
        return None

    params = {}
    if artist_name:
        params['artistName'] = artist_name
    if track_name:
        params['trackName'] = track_name

    api_endpoint = f'{API_BASE_URL}/api/audio/search'
    response = requests.get(api_endpoint, params=params)
    if response.status_code == 200:
        return response.json()  # Returns the parsed JSON response
    else:
        return None  # In case of a non-successful status code

def update_audio_file(audio_id, artist_name=None, track_name=None, file_url=None):
    update_fields = {}
    if artist_name is not None:
        update_fields['artistName'] = artist_name
    if track_name is not None:
        update_fields['trackName'] = track_name
    if file_url is not None:
        update_fields['fileUrl'] = file_url

    if not update_fields:
        print("No update fields provided.")
        return None

    api_endpoint = f'{API_BASE_URL}/api/audio/edit/{audio_id}'
    response = requests.put(api_endpoint, json=update_fields)
    return response.json()

def delete_audio_file(id):
    response = requests.delete(f'{API_BASE_URL}/api/audio/delete/{id}')
    return response.json()

def login(username, password):
    response = requests.post(f"{API_BASE_URL}/api/login", json={"username": username, "password": password})
    if response.status_code == 200:
        return True
    else:
        return False

def register(username, password):
    print(f"Registering user {username} with password {password}")
    response = requests.post(f"{API_BASE_URL}/api/register", json={"username": username, "password": password})
    print(response)
    if response.status_code == 201:
        return True
    else:
        return False