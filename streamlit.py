import streamlit as st
from PIL import Image

from test import auth, media_download, encode_image, image_gen, album_gen, video_gen

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
