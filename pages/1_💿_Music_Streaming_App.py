import streamlit as st
from api_calls import create_uuid, upload_file_to_gcs, send_to_api, fetch_audio_files, search_audio_files, login, register

st.set_page_config(
    page_title="Music Streaming App",
    page_icon="💿",
)

st.title('💿 Music Streaming App')

def login_page():
    st.title("Login")
    username = st.text_input("Username", key="client_username")
    password = st.text_input("Password", type="password", key="client_password")

    if st.button("Login"):
        if login(username, password):
            st.success("Logged in successfully!")
            return True
        else:
            st.error("Invalid username or password.")
            return False

def register_page():
    st.title("Register")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    confirm_password = st.text_input("Confirm Password", type="password")

    if st.button("Register"):
        if password != confirm_password:
            st.error("Passwords do not match.")
        else:
            if register(username, password):
                st.success("User registered successfully!")
            else:
                st.error("An error occurred.")

# Add authentication check before rendering the main content
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    # Display login and registration options
    tab1, tab2 = st.tabs(["Login", "Register"])

    with tab1:
        if login_page():
            st.session_state.logged_in = True
            st.rerun()

    with tab2:
        register_page()
else: 
    tab1, tab2, tab3 = st.tabs(["Stream", "Search", "Upload"])

    with tab1:
        # sort by most recent
        sort = st.selectbox('Sort by', ['Recently Uploaded', 'Artist Name', 'Track Name'])
        if sort == 'Recently Uploaded':
            audio_files = fetch_audio_files()
            for file in audio_files['data']:
                st.markdown(f"### Artist: {file['artistName']} | Track: {file['trackName']}")
                st.audio(file['fileUrl'])
                st.markdown('---')
        elif sort == 'Artist Name':
            audio_files = fetch_audio_files(sort_by='artistName', order='asc')
            for file in audio_files['data']:
                st.markdown(f"### Artist: {file['artistName']} | Track: {file['trackName']}")
                st.audio(file['fileUrl'])
                st.markdown('---')
        elif sort == 'Track Name':
            audio_files = fetch_audio_files(sort_by='trackName', order='asc')
            for file in audio_files['data']:
                st.markdown(f"### Artist: {file['artistName']} | Track: {file['trackName']}")
                st.audio(file['fileUrl'])
                st.markdown('---')

    with tab2:
        # Search by artist name or track name
        artist_name = st.text_input('Artist Name', key="search_artist")
        track_name = st.text_input('Track Name', key="search_track")
        search_button = st.button('Search', disabled=not (artist_name or track_name))

        if search_button:
            search_results = search_audio_files(artist_name, track_name)
            if search_results:
                if not search_results['data']:
                    st.warning('No results found')
                else:
                    for file in search_results['data']:
                        st.markdown(f"### Artist: {file['artistName']} | Track: {file['trackName']}")

                        st.audio(file['fileUrl'])
                        st.markdown('---')
            else:
                st.warning('No results found')

    with tab3:
        # Artist and Track name input
        artist_name = st.text_input('Artist Name', key="upload_artist")
        track_name = st.text_input('Track Name', key="upload_track")
        uploaded_file = st.file_uploader("Choose a file")

        submit_button = st.button('Submit Song', disabled=not (artist_name and track_name and uploaded_file and file))

        if submit_button and uploaded_file is not None and artist_name and track_name:
            file_extension = uploaded_file.name.split('.')[-1]
            if file_extension.lower() in ['mp3', 'ogg', 'wav']:
                file_url = upload_file_to_gcs(uploaded_file)
                st.success('File successfully uploaded')
                
                # Creating JSON object
                track_info = {
                    "artist_name": artist_name,
                    "track_name": track_name,
                    "file_url": file_url,
                }
                
                st.audio(file_url)
                send_to_api(track_info)
            else:
                st.warning("Please choose a file with .mp3, .ogg, or .wav extension.")
        elif submit_button:
            st.warning("Please enter an artist name, a track name, and choose a file to upload.")