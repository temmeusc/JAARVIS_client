## **Installation**

1. Install the required dependencies:

```
pip install -r requirements.txt

```

## **Usage**

1. Start the Streamlit application:

```
streamlit run Readme.py

```

2. Access the application in your web browser at `http://localhost:8501`.

## **Dependencies**

The project relies on the following dependencies:

- `streamlit`: For building the user interface.
- `requests`: For making HTTP requests to the API.
- `pandas`: For handling CSV files and data manipulation.
- `google-cloud-storage`: For interacting with Google Cloud Storage.
- `google-oauth2`: For authentication with Google Cloud Storage.

Make sure to install these dependencies using `pip install -r requirements.txt`.

## **API Calls**

The `api_calls.py` file contains functions for interacting with the Google Cloud Storage and the API endpoints:

- `create_uuid()`: Generates a unique identifier for audio files.
- `upload_file_to_gcs(file)`: Uploads an audio file to GCS and returns the public URL.
- `send_to_api(track_info)`: Sends audio file metadata to the API for storage in the database.
- `fetch_audio_files(page, sort_by, order, limit)`: Fetches audio files from the API with pagination and sorting options.
- `search_audio_files(artist_name, track_name)`: Searches for audio files based on artist name or track name.
- `update_audio_file(audio_id, artist_name, track_name, file_url)`: Updates the metadata of an audio file.
- `delete_audio_file(id)`: Deletes an audio file from the database.

It is configured by default to connect to the production API at https://dsci551-server-production.up.railway.app
You can change the value of API_BASE_URL in this file if you'd like to run the API server locally