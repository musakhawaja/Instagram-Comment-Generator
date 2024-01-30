import streamlit as st
from PIL import Image
from test import auth, media_download, encode_image, image_gen, album_gen, video_gen, image_caption, video_caption, album_caption
import tempfile
import shutil
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

st.title("Instagram Content Analysis")

if not st.session_state['logged_in']:
    username = st.text_input("Username")
    password = st.text_input("Password", type='password')
    if st.button("Login"):
        try:
            if auth(username, password):
                st.session_state['logged_in'] = True
                st.success("Logged in successfully")
            else:
                st.error("Login failed. Please check your credentials.")
        except Exception as e:
            st.error(f"Error during login: {e}")

if st.session_state['logged_in']:
    feature_choice = st.radio("Choose Feature", ("Generate Comments", "Generate Captions"))
    if feature_choice == "Generate Comments":
        content_type = st.radio("Select Content Type", ('Photo', 'Reel', 'Album'))
        url = st.text_input("Enter the Instagram URL")

        if st.button("Analyze Content"):
            try:
                media_path = media_download(url, content_type)

                if content_type == 'Photo':
                    base64_image = encode_image(media_path)
                    comments = image_gen(base64_image)
                elif content_type == 'Reel':
                    comments = video_gen(media_path)
                elif content_type == 'Album':
                    path_strings = [str(path) for path in media_path]
                    comments = album_gen(path_strings)

                st.text_area("Generated Comments", comments, height=300)
            except Exception as e:
                st.error(f"An error occurred: {e}")
    elif feature_choice == "Generate Captions":
        content_type = st.radio("Select Content Type for Captions", ('Photo', 'Reel', 'Album'))
        url = st.text_input("Enter the Instagram URL or Upload Content")
        uploaded_files = st.file_uploader("Or Upload Files", accept_multiple_files=True, type=["jpg", "jpeg", "png", "mp4"])
        if st.button("Analyze Content"):
            try:
                if url:
                    media_path = media_download(url, content_type)
                else:
                    if content_type in ['Photo', 'Reel']:
                        # Save the uploaded file to a temporary file
                        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp_file:
                            shutil.copyfileobj(uploaded_files[0], tmp_file)
                            tmp_file_path = tmp_file.name
                        media_path = tmp_file_path

                    elif content_type == 'Album' and len(uploaded_files) > 1:
                        media_path = []
                        for uploaded_file in uploaded_files:
                            # Save each uploaded file in the album to a temporary file
                            with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp_file:
                                shutil.copyfileobj(uploaded_file, tmp_file)
                                media_path.append(tmp_file.name)

                if content_type == 'Photo':
                    base64_image = encode_image(media_path)
                    comments = image_caption(base64_image)
                elif content_type == 'Reel':
                    comments = video_caption(media_path)
                elif content_type == 'Album':
                    path_strings = [str(path) for path in media_path]
                    comments = album_caption(path_strings)

                st.text_area("Generated Comments", comments, height=300)
            except Exception as e:
                st.error(f"An error occurred: {e}")

        
        
