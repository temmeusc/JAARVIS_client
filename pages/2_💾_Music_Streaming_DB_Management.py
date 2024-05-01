import streamlit as st
import requests
import pandas as pd
from api_calls import upload_file_to_gcs, send_to_api, fetch_audio_files, search_audio_files, update_audio_file, delete_audio_file, login, register

st.set_page_config(
    page_title="Music Streaming Database Management",
    page_icon="💾",
)

st.title("💾 Music Streaming Database Management")


def login_page():
    st.title("Login")
    username = st.text_input("Username", key="db_manager_username")
    password = st.text_input("Password", type="password", key="db_manager_password")

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
            st.experimental_rerun()

    with tab2:
        register_page()

else:

    tab1, tab2, tab3, tab4 = st.tabs(["View Entries", "Upload Entries", "Edit Entries", "Delete Entries"])

    with tab1:
        page = st.number_input("Page Number", min_value=1, value=1)
        entries_per_page = st.selectbox("Entries per page", [10, 25, 50, 100], index=1)
        view_button = st.button("View Audio Files", disabled=not entries_per_page and not page)
        if view_button:
            result = fetch_audio_files(page, limit=entries_per_page)
            if result['success']:
                data = result['data']
                # rename columns artistName to Artist Name, trackName to Track Name, fileUrl to URL, collection_tag to Collection Number, _id to Track ID
                for item in data:
                    item['Artist Name'] = item.pop('artistName')
                    item['Track Name'] = item.pop('trackName')
                    item['URL'] = item.pop('fileUrl')
                    item['Collection Number'] = item.pop('collection_tag')
                    item['Track ID'] = item.pop('_id')
                    item['Upload Date'] = item.pop('created_at', None)
                df = pd.DataFrame(data)
                st.dataframe(df)
                csv = df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    "Download as .csv",
                    csv,
                    "output.csv",
                    "text/csv",
                    key='download-csv'
                )
            else:
                st.error("Failed to fetch audio files.")


    with tab2:
        st.header("Upload Audio File")
        # Artist and Track name input
        artist_name = st.text_input('Artist Name', key="upload_artist")
        track_name = st.text_input('Track Name', key="upload_track")
        uploaded_file = st.file_uploader("Choose a file", key="upload_from_db_manager")

        submit_button = st.button('Submit Song', disabled=not (artist_name and track_name and uploaded_file))

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

        st.header("Bulk Upload via .csv")
        # Upload CSV file
        uploaded_file = st.file_uploader("Upload a .csv file with columns 'artistName', 'trackName', and 'fileUrl' to upload multiple audio files.")
        upload_button = st.button("Upload CSV", disabled=not uploaded_file)

        if upload_button:
            df = pd.read_csv(uploaded_file)
            # make sure the columns are named artistName, trackName, fileUrl
            if not all(col in df.columns for col in ['artistName', 'trackName', 'fileUrl']):
                st.error("Please make sure the .csv file has columns named 'artistName', 'trackName', and 'fileUrl'.")
            else:
                try:
                    for index, row in df.iterrows():
                        track_info = {
                            'artist_name': row.get('artistName', ''),
                            'track_name': row.get('trackName', ''),
                            'file_url': row.get('fileUrl', '')
                        }
                        result = send_to_api(track_info)
                        if result['success']:
                            st.success(f"Uploaded audio file for {track_info['artist_name']} - {track_info['track_name']}")
                        else:
                            st.error(f"Failed to upload audio file for {track_info['artist_name']} - {track_info['track_name']}")
                except Exception as e:
                    st.error(f"Failed to upload audio files: {e}")

    with tab3:
        st.header("Edit Audio File")
        track_id = st.text_input("Track ID to Edit", key="edit_id")
        artist_name = st.text_input("Updated Artist Name", key="edit_artist") or None
        track_name = st.text_input("Updated Track Name", key="edit_track") or None
        file_url = st.text_input("Updated File URL", key="edit_url") or None
        edit_button = st.button("Edit Audio File", disabled=not (artist_name or file_url or track_name))

        if edit_button:
            result = update_audio_file(track_id, artist_name, track_name, file_url)
            if result['success']:
                st.success(f"Updated audio file with ID {track_id}")
            else:
                st.error(f"Could not update audio file with ID {track_id} — check if the ID is correct.")

        st.header("Bulk Edit via .csv")
        edit_file = st.file_uploader("Upload a .csv file with columns 'trackID', 'artistName', 'trackName', and 'fileUrl' to edit multiple audio files.")
        edit_button = st.button("Edit Audio Files", disabled=not edit_file)
        
        if edit_button:
            df = pd.read_csv(edit_file)
            if not all(col in df.columns for col in ['trackID', 'artistName', 'trackName', 'fileUrl']):
                st.error("Please make sure the .csv file has columns named 'trackID', 'artistName', 'trackName', and 'fileUrl'.")
            else:
                try:
                    for index, row in df.iterrows():
                        result = update_audio_file(row.get('trackID', ''), row.get('artistName', ''), row.get('trackName', ''), row.get('fileUrl', ''))
                        if result['success']:
                            st.success(f"Updated audio file with ID {row.get('trackID', '')}")
                        else:
                            st.error(f"Could not update audio file with ID {row.get('trackID', '')} — check if the ID is correct.")
                except Exception as e:
                    st.error(f"Failed to update audio files: {e}")

    with tab4:
        st.header("Delete Audio File")
        id_to_delete = st.text_input("Audio File ID to Delete", key="delete_id")
        delete_button = st.button("Delete Audio File", disabled=not id_to_delete)
        
        if delete_button:
            result = delete_audio_file(id_to_delete)
            if result['success']:
                st.success(f"Deleted audio file with ID {id_to_delete}")
            else:
                st.error(f"Could not delete audio file with ID {id_to_delete} — check if the ID is correct.")
        
        st.header("Bulk Delete via .csv")
        delete_file = st.file_uploader("Upload a .csv file with a a single column named 'trackID' to delete multiple audio files.")
        delete_button = st.button("Delete Audio Files", disabled=not delete_file)

        if delete_button:
            df = pd.read_csv(delete_file)
            if 'trackID' not in df.columns:
                st.error("Please make sure the .csv file has a column named 'trackID'.")
            else:
                try:
                    for index, row in df.iterrows():
                        result = delete_audio_file(row.get('trackID', ''))
                        if result['success']:
                            st.success(f"Deleted audio file with ID {row.get('trackID', '')}")
                        else:
                            st.error(f"Could not delete audio file with ID {row.get('trackID', '')} — check if the ID is correct.")
                except Exception as e:
                    st.error(f"Failed to delete audio files: {e}")