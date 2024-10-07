import streamlit as st
import os
from cropper import processa_directory_con_maschere  # Import the functions from the cropper script

# Streamlit UI
st.title("Frame Mask Cropper")

# Form to input directories
with st.form("mask_cropper_form"):
    directory_input = st.text_input("Path della directory dei frame di input:")
    directory_maschere = st.text_input("Path della directory delle maschere di input:")
    directory_output = st.text_input("Path della directory di output per i frame croppati:")
    resize_maschera = st.checkbox("Ridimensiona la maschera se necessario", value=True)

    # Submit button
    submit_button = st.form_submit_button(label="Applica Maschere e Croppa")

# Process input if form is submitted
if submit_button:
    if directory_input and directory_maschere and directory_output:
        try:
            # Check if input and mask directories exist
            if not os.path.exists(directory_input):
                st.error(f"La directory dei frame di input non esiste: {directory_input}")
            elif not os.path.exists(directory_maschere):
                st.error(f"La directory delle maschere non esiste: {directory_maschere}")
            else:
                # Call the cropping function from the cropper script
                processa_directory_con_maschere(directory_input, directory_maschere, directory_output, resize_maschera)
                st.success(f"Cropping completato! Le immagini sono state salvate in: {directory_output}")
        except Exception as e:
            st.error(f"Si è verificato un errore: {str(e)}")
    else:
        st.error("Per favore, compila tutti i campi.")
