# main_streamlit.py

import os
import streamlit as st
from typing import List, Any, Dict
import shutil
import cv2
import numpy as np
import base64
from PIL import Image
import io
import zipfile
from datetime import datetime

from anomaly_generator import get_available_models, set_model, perform_inpainting
from mask_generator import generate_elliptical_mask

# Configurazione della pagina
st.set_page_config(
    page_title="Generatore di Anomalie",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("Generatore di Anomalie con Inpainting")

# Inizializzazione dello stato della sessione per le triplette e l'indice corrente
if 'triplets' not in st.session_state:
    st.session_state['triplets'] = []
if 'current_index' not in st.session_state:
    st.session_state['current_index'] = 0
if 'zip_files' not in st.session_state:
    st.session_state['zip_files'] = {}

# Directory permanente per salvare le immagini
SAVE_DIR = "saved_images"
SOURCE_DIR = os.path.join(SAVE_DIR, "source")
MASK_DIR = os.path.join(SAVE_DIR, "mask")
GENERATED_DIR = os.path.join(SAVE_DIR, "generated")

# Creazione delle directory se non esistono
os.makedirs(SOURCE_DIR, exist_ok=True)
os.makedirs(MASK_DIR, exist_ok=True)
os.makedirs(GENERATED_DIR, exist_ok=True)

# Funzione per salvare i file caricati in una directory
def save_uploaded_files(uploaded_files, save_dir):
    saved_files = []
    for uploaded_file in uploaded_files:
        file_path = os.path.join(save_dir, uploaded_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        saved_files.append(file_path)
    return saved_files

# Callback functions per la navigazione
def go_back():
    if st.session_state['current_index'] > 0:
        st.session_state['current_index'] -= 1

def go_forward():
    if st.session_state['current_index'] < len(st.session_state['triplets']) - 1:
        st.session_state['current_index'] += 1

# Funzione per convertire un'immagine numpy array in base64
def image_to_base64(img):
    _, buffer = cv2.imencode('.png', img)
    img_bytes = buffer.tobytes()
    img_base64 = base64.b64encode(img_bytes).decode()
    return img_base64

# Funzione per creare un file zip in memoria
def create_zip_in_memory(directory: str) -> bytes:
    mem_zip = io.BytesIO()
    with zipfile.ZipFile(mem_zip, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
        for root, _, files in os.walk(directory):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, directory)
                zf.write(file_path, arcname)
    mem_zip.seek(0)
    return mem_zip.read()

# Funzione per generare le triplette e memorizzarle nello stato della sessione
def generate_anomaly_streamlit(input_images: List[str],
                               mask_parameters: Dict[str, Any],
                               anomaly_kwargs: Dict[str, Any],
                               inpainting_params: Dict[str, Any],
                               output_dirs: Dict[str, str]):
    triplet_images = []

    for index, input_image in enumerate(input_images):
        st.write(
            f"Elaborazione dell'immagine {index + 1}/{len(input_images)}: {os.path.basename(input_image)}")

        # Parametri per la maschera
        current_mask_parameters = mask_parameters.copy()
        current_mask_parameters.update({
            "input_image_path": input_image,
            "output_image_path": os.path.join(output_dirs['source'], f"{index}.png"),
            "output_mask_path": os.path.join(output_dirs['mask'], f"{index}.png"),
        })

        # Generazione della maschera
        generate_elliptical_mask(**current_mask_parameters)

        # Definizione dei prompt
        prompt = (
            f"(White-painted metal surface with realistic scratches:{anomaly_kwargs['White-painted metal surface with realistic scratches']}), "
            f"(scratches revealing underlying bare metal:{anomaly_kwargs['scratches revealing underlying bare metal']}), "
            f"(aged and worn paint with chipping and peeling:{anomaly_kwargs['aged and worn paint with chipping and peeling']}), "
            f"(highly detailed texture with fine imperfections:{anomaly_kwargs['highly detailed texture with fine imperfections']}), "
            f"photorealistic, ultra high resolution, sharp focus, realistic lighting, metallic sheen, macro photography"
        )

        negative_prompt = "(blurry), (low quality), (distortions), (unnatural colors), (non-metal elements), (concept art), (abstract), (digital artifacts), (overexposed), (underexposed), (noise), (grainy), (low resolution), (watermark), (text), (people), (animals)"

        init_image_path = os.path.join(output_dirs['source'], f"{index}.png")
        mask_image_path = os.path.join(output_dirs['mask'], f"{index}.png")
        output_image_path = os.path.join(output_dirs['generated'], f"{index}.png")

        # Parametri per inpainting
        inpainting_payload = {
            "prompt": prompt,
            "negative_prompt": negative_prompt,
            "seed": inpainting_params.get("random_seed", -1),
            "cfg_scale": inpainting_params.get("cfg_scale", 7.0),
            "denoising_strength": inpainting_params.get("denoising_strength", 0.75),
            "steps": inpainting_params.get("steps", 100),
            "sampler_index": inpainting_params.get("sampler_index", "Euler a")
        }

        perform_inpainting(
            init_image_path=init_image_path,
            mask_image_path=mask_image_path,
            output_image_path=output_image_path,
            **inpainting_payload
        )

        # Lettura delle immagini per la triplette
        try:
            source_img = cv2.imread(init_image_path)
            mask_img = cv2.imread(mask_image_path)
            generated_img = cv2.imread(output_image_path)

            if source_img is None or mask_img is None or generated_img is None:
                raise ValueError("Una delle immagini generate è vuota.")

            # Converti da BGR a RGB
            source_img = cv2.cvtColor(source_img, cv2.COLOR_BGR2RGB)
            mask_img = cv2.cvtColor(mask_img, cv2.COLOR_BGR2RGB)
            generated_img = cv2.cvtColor(generated_img, cv2.COLOR_BGR2RGB)

            # Converti le immagini in base64
            source_b64 = image_to_base64(source_img)
            mask_b64 = image_to_base64(mask_img)
            generated_b64 = image_to_base64(generated_img)

            # Aggiungi la triplette alla lista
            triplet_images.append({
                "source": source_b64,
                "mask": mask_b64,
                "generated": generated_b64
            })

        except Exception as e:
            st.error(f"Errore nella lettura delle immagini per la triplette {index + 1}: {e}")

    # Memorizza le triplette nello stato della sessione
    st.session_state['triplets'] = triplet_images
    st.session_state['current_index'] = 0

    # Creazione dei file ZIP in memoria
    with st.spinner("Creazione dei file ZIP..."):
        source_zip_bytes = create_zip_in_memory(output_dirs['source'])
        mask_zip_bytes = create_zip_in_memory(output_dirs['mask'])
        generated_zip_bytes = create_zip_in_memory(output_dirs['generated'])

        st.session_state['zip_files'] = {
            "source": source_zip_bytes,
            "mask": mask_zip_bytes,
            "generated": generated_zip_bytes
        }

# Inizio del form
with st.form("anomaly_form"):
    st.header("Configurazione dei Parametri")

    # 1. Caricamento delle immagini
    uploaded_images = st.file_uploader(
        "Carica le Immagini di Input",
        type=["png", "jpg", "jpeg"],
        accept_multiple_files=True,
        help="Seleziona una o più immagini da elaborare."
    )

    if uploaded_images:
        st.write(f"**Immagini Caricate:** {len(uploaded_images)}")
    else:
        st.warning("Per favore carica almeno un'immagine.")

    st.markdown("---")

    # 2. Selezione del Modello
    models = get_available_models()
    if not models:
        st.error("Nessun modello disponibile.")
        st.stop()

    model_titles = [model['title'] for model in models]
    selected_model = st.selectbox("Seleziona il Modello", options=model_titles, index=0)

    # 3. Parametri per la Maschera
    st.subheader("Parametri per la Maschera Ellittica")

    scaling_factor = st.slider(
        "Fattore di Scala",
        min_value=0.1,
        max_value=1.0,
        value=0.1,
        step=0.05,
        help="Fattore di scala per la dimensione dell'ellisse."
    )

    eccentricity = st.slider(
        "Eccentricità",
        min_value=0.0,
        max_value=0.99,
        value=0.3,
        step=0.01,
        help="Eccentricità dell'ellisse."
    )

    # Utilizzare `st.number_input` con un valore di default e interpretare 0 come None
    center_x_input = st.number_input(
        "Centro X",
        min_value=0,
        max_value=1024,  # Puoi adattare in base alle dimensioni massime previste
        value=0,
        step=1,
        format="%d",
        help="Coordinata X del centro dell'ellisse. Imposta a 0 per generare casualmente."
    )

    center_y_input = st.number_input(
        "Centro Y",
        min_value=0,
        max_value=1024,
        value=0,
        step=1,
        format="%d",
        help="Coordinata Y del centro dell'ellisse. Imposta a 0 per generare casualmente."
    )

    angle = st.slider(
        "Angolo (gradi)",
        min_value=0,
        max_value=360,
        value=45,
        step=1,
        help="Angolo di orientamento dell'ellisse."
    )

    allow_out_of_bounds = st.checkbox(
        "Permetti Fuoriuscita dai Bordi",
        value=False,
        help="Consente alla maschera di fuoriuscire dai bordi dell'immagine."
    )

    retry_on_failure = st.checkbox(
        "Riprova in Caso di Fallimento",
        value=True,
        help="Riprova a generare la maschera se esce dai bordi."
    )

    max_attempts = st.number_input(
        "Numero Massimo di Tentativi",
        min_value=1,
        max_value=10000,
        value=100,
        step=1,
        help="Numero massimo di tentativi per generare una maschera valida."
    )

    st.markdown("---")

    # 4. Parametri per l'Inpainting
    st.subheader("Parametri per l'Inpainting")

    col1, col2 = st.columns(2)

    with col1:
        white_painted_scratches = st.slider(
            "Superficie Metallica Dipinta Bianca con Graffi Realistici",
            min_value=0.0,
            max_value=5.0,
            value=1.5,
            step=0.1,
            help="Intensità dei graffi realistici sulla superficie metallica dipinta bianca."
        )

        aged_paint = st.slider(
            "Vernice Invecchiata e Logora",
            min_value=0.0,
            max_value=5.0,
            value=1.2,
            step=0.1,
            help="Intensità della vernice invecchiata e logora."
        )

    with col2:
        scratches_bare_metal = st.slider(
            "Graffi che Rivelano il Metallo Nudo Sottostante",
            min_value=0,
            max_value=50,
            value=15,
            step=1,
            help="Numero di graffi che rivelano il metallo nudo sottostante."
        )

        detailed_texture = st.slider(
            "Texture Dettagliata con Piccole Imperfezioni",
            min_value=0.0,
            max_value=5.0,
            value=1.0,
            step=0.1,
            help="Intensità della texture dettagliata con piccole imperfezioni."
        )

    random_seed = st.number_input(
        "Seed Casuale",
        min_value=-1,
        max_value=2147483647,
        value=-1,
        step=1,
        help="Seed per la generazione casuale. Usa -1 per un seed casuale."
    )

    st.markdown("---")

    # 5. Altri Parametri per Inpainting (opzionali)
    st.subheader("Parametri Avanzati per Inpainting")

    cfg_scale = st.slider(
        "CFG Scale",
        min_value=1.0,
        max_value=20.0,
        value=7.0,
        step=0.5,
        help="Bilanciamento tra prompt e generazione dell'immagine."
    )

    denoising_strength = st.slider(
        "Forza di Denoising",
        min_value=0.0,
        max_value=1.0,
        value=0.75,
        step=0.05,
        help="Forza di denoising applicata all'immagine."
    )

    steps = st.slider(
        "Numero di Passaggi (Steps)",
        min_value=1,
        max_value=500,
        value=100,
        step=1,
        help="Numero di passaggi per la generazione dell'immagine."
    )

    sampler_index = st.selectbox(
        "Sampler",
        options=["Euler a", "LMS", "Heun", "DPM2", "DPM2 a", "DPM++ 2S a", "DPM++ 2M", "DPM++ SDE"],
        index=0,
        help="Metodo di campionamento utilizzato per la generazione."
    )

    st.markdown("---")

    # 6. Pulsante per inviare il form
    submit_button = st.form_submit_button("Genera Anomalie")

# Funzione per creare un file zip in memoria
def create_zip_in_memory(directory: str) -> bytes:
    mem_zip = io.BytesIO()
    with zipfile.ZipFile(mem_zip, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
        for root, _, files in os.walk(directory):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, directory)
                zf.write(file_path, arcname)
    mem_zip.seek(0)
    return mem_zip.read()

# Se il form è stato inviato
if submit_button:
    if not uploaded_images:
        st.error("Per favore carica almeno un'immagine per procedere.")
    else:
        with st.spinner("Impostazione del modello..."):
            set_model(selected_model)

        # Salvataggio delle immagini caricate nella directory 'source'
        saved_input_images = save_uploaded_files(uploaded_images, SOURCE_DIR)

        # Preparazione dei parametri
        mask_parameters = {
            "scaling_factor": scaling_factor,
            "eccentricity": eccentricity,
            "center_x": center_x_input if center_x_input != 0 else None,
            "center_y": center_y_input if center_y_input != 0 else None,
            "angle": angle,
            "allow_out_of_bounds": allow_out_of_bounds,
            "retry_on_failure": retry_on_failure,
            "max_attempts": max_attempts
        }

        anomaly_kwargs = {
            "White-painted metal surface with realistic scratches": white_painted_scratches,
            "scratches revealing underlying bare metal": scratches_bare_metal,
            "aged and worn paint with chipping and peeling": aged_paint,
            "highly detailed texture with fine imperfections": detailed_texture
        }

        # Parametri aggiuntivi per inpainting
        inpainting_parameters = {
            "cfg_scale": cfg_scale,
            "denoising_strength": denoising_strength,
            "steps": steps,
            "sampler_index": sampler_index,
            "random_seed": random_seed  # Aggiunto per passare il seed
        }

        # Definizione delle directory di output
        output_dirs = {
            "source": SOURCE_DIR,
            "mask": MASK_DIR,
            "generated": GENERATED_DIR
        }

        # Generazione delle anomalie
        with st.spinner("Generazione delle anomalie in corso..."):
            generate_anomaly_streamlit(
                input_images=saved_input_images,
                mask_parameters=mask_parameters,
                anomaly_kwargs=anomaly_kwargs,
                inpainting_params=inpainting_parameters,
                output_dirs=output_dirs
            )
            st.success("Generazione completata!")

# Visualizzazione delle triplette con navigazione
if st.session_state['triplets']:
    triplets = st.session_state['triplets']
    current_index = st.session_state['current_index']

    def display_triplet(index):
        triplet = triplets[index]
        col1, col2, col3 = st.columns(3)

        # Decodifica delle immagini da base64
        source_img = base64.b64decode(triplet['source'])
        mask_img = base64.b64decode(triplet['mask'])
        generated_img = base64.b64decode(triplet['generated'])

        # Converti i bytes in immagini utilizzabili da st.image
        source_pil = Image.open(io.BytesIO(source_img))
        mask_pil = Image.open(io.BytesIO(mask_img))
        generated_pil = Image.open(io.BytesIO(generated_img))

        with col1:
            st.image(source_pil, caption="Immagine Sorgente", use_column_width=True)
        with col2:
            st.image(mask_pil, caption="Maschera", use_column_width=True)
        with col3:
            st.image(generated_pil, caption="Immagine Generata", use_column_width=True)

    # Layout per la navigazione centrata
    nav_col1, nav_col2, nav_col3 = st.columns([1, 2, 1])

    with nav_col1:
        st.button("⬅️ Indietro", on_click=go_back, key='back_button',
                  disabled=(st.session_state['current_index'] <= 0),
                  use_container_width=True)

    with nav_col2:
        st.markdown(
            f"""
            <div style="text-align: center;">
                <strong>Immagine {st.session_state['current_index'] + 1} di {len(triplets)}</strong>
            </div>
            """,
            unsafe_allow_html=True
        )

    with nav_col3:
        st.button("Avanti ➡️", on_click=go_forward, key='forward_button',
                  disabled=(st.session_state['current_index'] >= len(triplets) - 1),
                  use_container_width=True)

    # Mostra la triplette corrente
    display_triplet(st.session_state['current_index'])

    # Creazione e download dei file ZIP dopo la generazione
    # Creazione e download dei file ZIP dopo la generazione
    if st.session_state['zip_files']:
        st.markdown("---")
        # Rimuovi o commenta la seguente linea per eliminare il sottotitolo
        # st.subheader("Scarica le Immagini Generate")

        # Crea tre colonne per allineare i bottoni orizzontalmente
        col1, col2, col3 = st.columns(3)

        with col1:
            st.download_button(
                label="Scarica Immagini Sorgente ZIP",
                data=st.session_state['zip_files']['source'],
                file_name=f"Immagini_Sorgente_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip",
                mime="application/zip",
                use_container_width=True
            )

        with col2:
            st.download_button(
                label="Scarica Maschere ZIP",
                data=st.session_state['zip_files']['mask'],
                file_name=f"Maschere_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip",
                mime="application/zip",
                use_container_width=True
            )

        with col3:
            st.download_button(
                label="Scarica Immagini Generate ZIP",
                data=st.session_state['zip_files']['generated'],
                file_name=f"Immagini_Generate_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip",
                mime="application/zip",
                use_container_width=True
            )
