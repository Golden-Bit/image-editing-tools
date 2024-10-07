import streamlit as st
import os
import tempfile
from video_processing import extract_frames

# Streamlit UI
st.title("Video Frame Extractor")

# Use a form for input
with st.form("video_extractor_form"):
    uploaded_file = st.file_uploader("Upload video file", type=["mp4", "avi", "mov", "mkv"])
    start_sec = st.number_input("Start second:", min_value=0.0, step=0.1)
    end_sec = st.number_input("End second:", min_value=0.0, step=0.1)
    frame_rate = st.number_input("Frame rate (frames per second):", min_value=0.1, step=0.1)
    output_dir = st.text_input("Output directory path:")

    # Submit button inside the form
    submit_button = st.form_submit_button(label="Extract Frames")

# Handle form submission
if submit_button:
    if uploaded_file and output_dir:
        try:
            # Save the uploaded video to a temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_video:
                temp_video.write(uploaded_file.read())
                video_path = temp_video.name

            # Ensure output directory exists
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)

            # Call the function to extract frames
            extract_frames(video_path, start_sec, end_sec, frame_rate, output_dir)
            st.success(f"Frames extracted successfully to {output_dir}")

        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
    else:
        st.error("Please upload a video and provide a valid output directory.")
