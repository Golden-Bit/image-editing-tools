import streamlit as st
import os
from tiles_extractor import processa_directory, organize_tiles_by_position

# Streamlit UI
st.title("Image Tiles Extractor and Organizer")

# Form to input directories and parameters
with st.form("tiles_extractor_form"):
    directory_input = st.text_input("Path della directory di input delle immagini:")
    directory_output = st.text_input("Path della directory di output per i tasselli:")

    tassello_dim_larghezza = st.number_input("Larghezza del tassello (in pixel):", min_value=1, value=256)
    tassello_dim_altezza = st.number_input("Altezza del tassello (in pixel):", min_value=1, value=256)

    passo_orizzontale = st.number_input("Passo orizzontale (in pixel):", min_value=1, value=128)
    passo_verticale = st.number_input("Passo verticale (in pixel):", min_value=1, value=128)

    input_resize = st.checkbox("Ridimensiona immagine di input?", value=False)
    if input_resize:
        input_resize_larghezza = st.number_input("Larghezza di input (in pixel):", min_value=1)
        input_resize_altezza = st.number_input("Altezza di input (in pixel):", min_value=1)
        input_resize = (input_resize_larghezza, input_resize_altezza)
    else:
        input_resize = None

    output_resize = st.checkbox("Ridimensiona tasselli estratti?", value=False)
    if output_resize:
        output_resize_larghezza = st.number_input("Larghezza tasselli (in pixel):", min_value=1)
        output_resize_altezza = st.number_input("Altezza tasselli (in pixel):", min_value=1)
        output_resize = (output_resize_larghezza, output_resize_altezza)
    else:
        output_resize = None

    input_rotate = st.number_input("Rotazione dell'immagine di input (gradi):", min_value=0, max_value=360, value=0)
    if input_rotate == 0:
        input_rotate = None

    output_rotate = st.number_input("Rotazione dei tasselli estratti (gradi):", min_value=0, max_value=360, value=0)
    if output_rotate == 0:
        output_rotate = None

    submit_button = st.form_submit_button(label="Estrai Tasselli")

# If form is submitted
if submit_button:
    if directory_input and directory_output:
        try:
            tassello_dim = (tassello_dim_larghezza, tassello_dim_altezza)
            passo = (passo_orizzontale, passo_verticale)

            # Check if input directory exists
            if not os.path.exists(directory_input):
                st.error(f"La directory di input non esiste: {directory_input}")
            else:
                # Process the images and extract tiles
                processa_directory(directory_input, directory_output, tassello_dim, passo, input_resize, output_resize,
                                   input_rotate, output_rotate)
                st.success(f"Estrazione dei tasselli completata! I tasselli sono stati salvati in {directory_output}.")
        except Exception as e:
            st.error(f"Si è verificato un errore: {str(e)}")
    else:
        st.error("Per favore, compila tutti i campi.")

# Organizer section
st.header("Organizza Tasselli per Posizione")

# Directory input for tile organization
directory_to_organize = st.text_input("Path della directory di output per i tasselli estratti da organizzare:")
organize_button = st.button("Organizza Tasselli")

# Organize tiles by position if button clicked
if organize_button:
    if directory_to_organize:
        try:
            # Organize the tiles by position
            organize_tiles_by_position(directory_to_organize)
            st.success(f"Tasselli organizzati per posizione e salvati in: {directory_to_organize}_reverse")
        except Exception as e:
            st.error(f"Si è verificato un errore durante l'organizzazione: {str(e)}")
    else:
        st.error("Inserisci il percorso della directory dei tasselli da organizzare.")
