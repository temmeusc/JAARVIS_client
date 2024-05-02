import streamlit as st

st.set_page_config(
    page_title="Readme",
    page_icon="📄",
)

st.write("# DSCI 551 Final Project: Music Streaming App")

st.markdown(
    """
    ## Team Members
    - Tristan Rodman
    - James Temme
    - Zian Tang

    ## Project Description
    Our project is a Music Streaming App that allows users to upload, stream, search, and manage audio files. The app consists of three main components:
    - Two front-end websites, one for end users + one for database managers
    - Google Cloud Storage to store audio files
    - A middleware API to route requests from the front end and database administrator sites through a hash function
    - MongoDB database to store audio file information, running on EC2

    ## Planned Implementation (from original proposal)
    We plan to build a basic music streaming service. The front end experience will be a vertical feed of audio files that users have uploaded to the database, displaying track title and artist name. Users will be able to add their own submissions and see those appear at the top of the feed. It will be built with React.
    
    The database administrator experience will be a tabular data view that allows a data administrator to bulk edit or delete entries. It will be built with Streamlit.
    
    We’ll build a middleware API that will route requests from the front end and database administrator sites through a hash function and to a distributed MongoDB database.

    In the midterm progress report, we updated our plan to use Streamlit for both the front end and database administrator sites. We also decided to use Google Cloud Storage to store audio files and MongoDB to store audio file information.
    
    ## Architechture
    """
)

st.image("https://github.com/simulcast/dsci551-client/blob/main/architecture.png?raw=true.png", use_column_width=True)
st.markdown(
    """
    **User Interface (Streamlit App)**
    - The user-facing frontend is built using Streamlit, a Python library for creating interactive web applications.
    - There are two Streamlit pages
        - "Music Streaming App" (`1_💿_Music_Streaming_App.py`): Allows users to stream, search, and upload audio files.
        - "Music Streaming Database Management" (`2_💾_Music_Streaming_DB_Management.py`): Provides database management functionalities for administrators, such as viewing, uploading, editing, and deleting audio files.

    **Middleware (Flask Server)**
    - The Flask server (`main.py`) acts as an intermediary between the user interface and the database.
    - It exposes API endpoints for handling various operations related to audio files, such as uploading, listing, searching, editing, and deleting.
    - The middleware communicates with the database (MongoDB) to perform CRUD (Create, Read, Update, Delete) operations on audio metadata.

    **Cloud File Storage (Google Cloud GCS)**
    - When a user uploads an audio file, it is first uploaded to GCS, and the corresponding file URL is stored in the database.
    - The middleware interacts with GCS to handle file uploads and retrievals.
    - See future scope below for additional thoughts on improving GCS file management features.

    **Database (MongoDB)**
    - The MongoDB database is used to store audio metadata, such as artist name, track name, file URL, and collection information.
    - The middleware communicates with the MongoDB database to perform CRUD operations on audio metadata.
    - The database is organized into collections based on a hashing function that determines the collection name for each audio file.

    The flow of data and interactions between the components is as follows:
    - Users interact with the Streamlit user interface to stream, search, upload, edit, or delete audio files.
    - The Streamlit app sends requests to the Flask middleware server via API calls.
    - The Flask server processes the requests, interacts with the MongoDB database to perform the required operations, and returns the results back to the Streamlit app.
    - When an audio file is uploaded, the Flask server first uploads the file to Google Cloud Storage and obtains the file URL.
    - The file URL, along with other metadata, is then stored in the MongoDB database.
    - When a user requests to stream or download an audio file, the Streamlit app retrieves the file URL from the database and serves the file to the user.

    This architecture allows for a separation of concerns, with the user interface, middleware, file storage, and database each handling specific responsibilities.
    
    ## Implementation
    ### Middleware `main.py`
    The `main.py` file is the main server script for the Music Streaming App. It implements a Flask-based API that handles various endpoints for managing audio files and user authentication. The API communicates with a MongoDB database to store and retrieve audio file metadata and user information.

    **Database Connection**
    - The script establishes a connection to a MongoDB database using the provided connection URL.
    - It uses the pymongo library to interact with the database.


    **Hash Function**
    - The `hash_function()` is a utility function that generates a hash value based on the artist name and track name. It has the following steps...
        - Extract Initials from Names
            - Artist Initials: The function first looks at the artist's name, takes the first letter of the first word and the first letter of the last word to form the artist initials. 
                - For example, from "Taylor Swift", it takes 'T' from "Taylor" and 'S' from "Swift" to make "TS".
            - Track Initials: Similarly, it takes the track's name and extracts the first letter of the first word and the first letter of the last word to form the track initials.
                - For example, from "Love Story", it takes 'L' from "Love" and 'S' from "Story" to make "LS".
        - Convert Initials to Numbers
            - The function then converts these letters (initials) into their ASCII numerical values.
            - Sum the ASCII Values
            - The ASCII values of both the artist initials and the track initials are summed up to get a total number.
        - Decide the Storage Option
            - Even/Odd Check: If this total number is even, the data will be stored in JSON file 0. If it's odd, the data will be stored in JSON file 1.
            - Error Check: If somehow both the artist's and the track's names are missing, leading to a total sum of 0, the function will print an error message indicating the absence of names.



    **JSON Serialization**
    - The `jsonify_mongo()` function is a helper function that converts MongoDB document objects to JSON-serializable format.
    - It takes a list of dictionaries representing MongoDB documents and converts any ObjectId fields to string format.
    - This function is used to prepare the response data for API endpoints that return MongoDB documents.


    **API Endpoints**

    `/api/audio/upload (POST)`
    - Handles the upload of a new audio file.
    - Expects a JSON payload containing the artist name, track name, and file URL.
    - Generates a hash value using the hash_function() based on the artist name and track name.
    - Inserts the audio file metadata into the corresponding MongoDB collection based on the hash value.
    - Returns a JSON response indicating the success status and the uploaded audio file metadata.


    `/api/audio/list (GET)`
    - Retrieves a list of audio files from the database.
    - Supports pagination using the page and limit query parameters.
    - Allows sorting the results based on the sort_by query parameter (default: "created_at") and the order query parameter (default: descending).
    - Fetches the audio file metadata from the MongoDB database based on the specified pagination and sorting parameters.
    - Returns a JSON response containing the list of audio file metadata.


    `/api/audio/search (GET)`
    - Performs a search for audio files based on the provided artist name and/or track name.
    - Expects the artistName and/or trackName query parameters.
    - Searches the MongoDB database for audio file metadata matching the provided search criteria.
    - Supports pagination using the page and limit query parameters.
    - Returns a JSON response containing the matching audio file metadata.


    `/api/audio/edit/<id> (PUT)`
    - Updates the metadata of an existing audio file.
    - Expects the audio file ID as a URL parameter.
    - Accepts a JSON payload containing the updated artist name, track name, and/or file URL.
    - Updates the corresponding audio file metadata in the MongoDB database.
    - Returns a JSON response indicating the success status and a message.

    `/api/audio/delete/<id> (DELETE)`
    - Deletes an audio file from the database.
    - Expects the audio file ID as a URL parameter.
    - Removes the corresponding audio file metadata from the MongoDB database.
    - Returns a JSON response indicating the success status and a message.


    `/api/register (POST)`
    - Handles user registration.
    - Expects a JSON payload containing the username and password.
    - Checks if the username already exists in the database.
    - If the username is available, hashes the password using bcrypt and stores the user information in the MongoDB database.
    - Returns a JSON response indicating the success status and a message.


    `/api/login (POST)`
    - Handles user login.
    - Expects a JSON payload containing the username and password.
    - Retrieves the user information from the MongoDB database based on the provided username.
    - Compares the provided password with the stored hashed password using bcrypt.
    - If the credentials are valid, returns a JSON response indicating the success status and a message.
    - If the credentials are invalid, returns a JSON response indicating the failure status and an error message.

    **Error Handling**
    - Each API endpoint includes error handling using try-except blocks.
    - If an exception occurs during the execution of an endpoint, an appropriate error response is returned indicating the failure status and an error message.


    **Cross-Origin Resource Sharing (CORS)**
    - The API includes Cross-Origin Resource Sharing (CORS) support using the flask_cors library.
    - CORS allows the API to be accessed from different origins (domains) in a web browser.


    **Server Configuration**
    - The Flask server is configured to run in debug mode (`debug=True`) for development purposes.
    - It is set to listen on all available network interfaces (`host='0.0.0.0'`).
    - The server port is determined by the environment variable `PORT` if available, otherwise it defaults to port `5000`.

    ### Client Application `1_💿_Music_Streaming_App.py`
    This Streamlit page represents the main user interface for the Music Streaming App. It allows users to stream, search, and upload audio files.

    **Authentication**
    - The page includes authentication checks using the `login_page()` and `register_page()` functions from `api_calls.py`.
    - If the user is not logged in, they are redirected to the login page, where they can enter their username and password to authenticate.
    - If the user doesn't have an account, they can navigate to the registration page to create a new account by providing a username and password.
    - Once authenticated, the user is redirected back to the main Music Streaming App page, where they can access the "Stream", "Search", and "Upload" tabs.
    - The authentication status is stored in the Streamlit session state (st.session_state.logged_in) to persist across page reloads.
    - If the user clicks the "Logout" button, their authentication status is cleared, and they are redirected back to the login page.

    **Stream**
    - Users can browse and stream audio files.
    - The files are sorted based on the selected option (Recently Uploaded, Artist Name, or Track Name).
    - The audio files are fetched from the API using the `fetch_audio_files()` function from `api_calls.py`.
    - The retrieved audio files are displayed in a user-friendly format, showing the artist name, track name, and an audio player for each file.
    - Users can click on the audio player to play, pause, or seek within the audio file.

    **Search**
    - Users can search for audio files by entering the artist name and/or track name.
    - The search results are fetched from the API using the `search_audio_files()` function from `api_calls.py`.

    **Upload**
    - Users can upload a new audio file by providing the artist name, track name, and selecting the audio file.
    - The file is uploaded to Google Cloud Storage using the `upload_file_to_gcs()` function from `api_calls.py` and the metadata is sent to the API using the `send_to_api()` function.  

    ### DB Manager Application `2_💾_Music_Streaming_DB_Management.py`

    This Streamlit page serves as a database management interface for administrators. It allows administrators to view, upload, edit, and delete audio file entries in the database.

    **Authentication**
    - The page includes authentication checks using the `login_page()` and `register_page()` functions from `api_calls.py`.
    - If the user is not logged in, they are redirected to the login page, where they can enter their username and password to authenticate.
    - If the user doesn't have an account, they can navigate to the registration page to create a new account by providing a username and password.
    - Once authenticated, the user is redirected back to the main Music Streaming App page, where they can access the "Stream", "Search", and "Upload" tabs.
    - The authentication status is stored in the Streamlit session state (st.session_state.logged_in) to persist across page reloads.
    - If the user clicks the "Logout" button, their authentication status is cleared, and they are redirected back to the login page.
    
    **View**
    - Administrators can view the list of audio files in the database.
    - They can specify the page number and the number of entries per page.
    - The audio files are fetched from the API using the `fetch_audio_files()` function from api_calls.py.
    - The retrieved data is displayed in a table format, and administrators can download the data as a CSV file.
    
    **Upload**
    - Administrators can upload new audio files individually or in bulk using a CSV file.
    - For individual uploads, they provide the artist name, track name, and select the audio file.
    - The file is uploaded to Google Cloud Storage using the `upload_file_to_gcs()` function, and the metadata is sent to the API using the `send_to_api()` function.
    - For bulk uploads, administrators can upload a CSV file containing the artist name, tracke name, and file URL, and each entry is processed and uploaded to the API.
    
    **Edit**
    - Administrators can edit existing audio file entries.
    - They can provide the track ID and update the artist name, track name, and/or file URL.
    - The updates are sent to the API using the `update_audio_file()` function from `api_calls.py`.
    - Administrators can also perform bulk edits by uploading a CSV file containing the track IDs and the updated information.
    
    **Delete**
    - Administrators can delete audio file entries by providing the track ID.
    - The deletion is performed by sending a request to the API using the `delete_audio_file()` function from `api_calls.py`.
    - Administrators can also perform bulk deletions by uploading a CSV file containing the track IDs to be deleted.
    
    ### API Helper `api_calls.py`
    This module contains helper functions for interacting with the API, including functions for user authentication (login and registration) and various operations related to audio files (upload, fetch, search, update, delete).
    - `create_uuid()` Generates a random UUID and returns it as a 32-character string without hyphens.
    - `upload_file_to_gcs(file)` Uploads a file to Google Cloud Storage (GCS) using the provided service account credentials. It generates a unique filename using create_uuid() and returns the public URL of the uploaded file.
    - `send_to_api(track_info)` Sends a POST request to the API endpoint /api/audio/upload with the provided track information (artist name, track name, and file URL) as a JSON payload. It returns the parsed JSON response from the API.
    - `fetch_audio_files(page=1, sort_by='created_at', order='desc', limit=10)` Fetches audio files from the API endpoint /api/audio/list with optional pagination and sorting parameters. It returns the parsed JSON response from the API.
    - `search_audio_files(artist_name='', track_name='')` Searches for audio files based on the provided artist name and/or track name by sending a GET request to the API endpoint /api/audio/search. It returns the parsed JSON response from the API.
    - `update_audio_file(audio_id, artist_name=None, track_name=None, file_url=None)` Updates an audio file with the specified audio_id by sending a PUT request to the API endpoint /api/audio/edit/{audio_id} with the provided update fields (artist name, track name, and/or file URL) as a JSON payload. It returns the parsed JSON response from the API.
    - `delete_audio_file(id)` Deletes an audio file with the specified id by sending a DELETE request to the API endpoint /api/audio/delete/{id}. It returns the parsed JSON response from the API.
    - `login(username, password)` Sends a POST request to the API endpoint /login with the provided username and password as a JSON payload. It returns True if the login is successful (status code 200), otherwise it returns False.
    - `register(username, password)` Sends a POST request to the API endpoint /register with the provided username and password as a JSON payload. It returns True if the registration is successful (status code 201), otherwise it returns False.
    
    ### Requirements and Dependencies `requirements.txt`
    The `requirements.txt` file lists all the Python packages required to run the Music Streaming App. It includes the following packages:
    - Flask==3.0.3
    - Flask_Cors==4.0.0
    - pandas==2.0.0
    - protobuf>=3.20,<5
    - pymongo==4.6.3
    - modules==1.0.0
    - Requests==2.31.0
    - streamlit==1.32.0
    - Werkzeug==3.0.2
    - google-cloud-storage>=1.45.0

    ## Learning Outcomes
    **Challenges Faced**
    - Setting up the MongoDB database and configuring the connection to the Flask server.
    - Implementing user authentication and session management in the Streamlit app.
    - Handling file uploads to Google Cloud Storage and storing file URLs in the database.
    - Managing the flow of data between the Streamlit app, Flask server, Google Cloud Storage, and MongoDB database.
    - Implementing CRUD operations for audio files in the middleware API.
    - Handling errors and exceptions in API endpoints and user interactions.

    ## Individual Contribution
    - Tristan Rodman: Worked on the Streamlit front-end application, including the user authentication, streaming, search, and upload functionalities. Also contributed to the API helper functions and documentation.
    - James Temme: Worked on MongoDB setup, database connection, and Flask middleware. Also contributed to the client API helper functions and documentation.
    - Zian Tang: Worked on hash function and Flask middleware. Also contributed to the client API helper functions and documentation.

    ## Conclusion
    The Music Streaming App project provided us with valuable experience in building a full-stack web application using Streamlit, Flask, MongoDB, and Google Cloud Storage. We learned how to design and implement user interfaces, middleware APIs, and database interactions to create a functional and user-friendly application. The project helped us improve our skills in web development, API design, database management, and cloud storage integration. We faced various challenges during the development process, but we were able to overcome them through collaboration, problem-solving, and continuous learning. Overall, the project was a great learning experience that allowed us to apply our knowledge and skills in a real-world scenario.

    ## Future Scope
    
    **Better GCS File Management**
    - Add functionality to delete files from GCS when an audio file is deleted from the database based on the file URL.
    - Implement a mechanism to handle file versioning or updates in GCS.
    - Use environment variables for GCS bucket name and service account file path.
    - Add error handling for GCS file upload failures.
    - Implement file size restrictions and validation for uploaded files.

    **More Secure Authentication**
    - Implement password hashing using sha256 over bcrypt for better security.
    - Add password complexity requirements and validation during registration.
    - Implement password reset functionality using email verification.

    **User Roles and Permissions**
    - Implement role-based access control (RBAC) to differentiate between regular users and administrators.
    - Define different permissions for each role, such as viewing, uploading, editing, and deleting audio files.
    - Add an admin panel to manage user roles and permissions.
    - Secure API endpoints based on user roles and permissions.
    - Implement user authentication using JWT tokens for better security.

    **Enhanced MongoDB Sharding for Scalability**
    - As our Music Streaming App grows in user base and data volume, scaling our database efficiently becomes crucial. To address this, we plan to implement sharding directly through MongoDB.
    - Sharding will allow us to distribute our data across multiple servers, enhancing our app's performance and scalability by reducing the load on any single server and increasing fault tolerance.
    - **Implementation Strategy**
        - Shard Key Selection
            - We will identify appropriate shard keys for our main collections
            - A good shard key should have high cardinality, write distribution, and query isolation. [`file_id` and `upload_date` make sense for our audio collections]
        - Sharded Cluster
            - Our Mongo deployment will transition from a single replica set to a sharded cluster consisting of several shards (each of which are a replica).
            - This setup will involve shard servers, config servers, and query routers
            - We will deploy the mongos service as part of our Flask middleware, allowing our application to interact transparently with our sharded database [MusicalChairs]
            - The mongos instances will route queries to the appropriate shards & manage the data distribution complexity
        - Data Migration and Balancing
            - After initializing the sharded cluster, we will migrate existing data to the our new cluster
            - MongoDB’s sharding mechanism automatically balances data across shards to ensure even distribution
        - Query Optimization
            - Post-migration, we will optimize queries to ensure they are making efficient use of indexes and minimizing cross-shard operations
        - Maintenance, Monitoring, Security & Access Control
            - By implementing sharding, we aim to enhance our application’s scalability and performance, ensuring that it remains robust and responsive as it scales
        - Security and Access Control
            - Shards will be secured using role-based access controls, ensuring that only authorized services and users have access to sensitive data
            - All communications between cluster components will be encrypted to prevent unauthorized data access
            - This strategy supports future growth and improves the resilience and efficiency of our database operations
    """
)