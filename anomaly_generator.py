import requests
import base64
import json

# URL del server API
API_URL = 'http://localhost:7861'

# Funzione per caricare e codificare un'immagine in Base64 senza prefisso
def load_image_base64(file_path):
    with open(file_path, "rb") as f:
        encoded_string = base64.b64encode(f.read()).decode()
        return encoded_string

# 1. Ottenere la lista dei modelli disponibili
def get_available_models():
    response = requests.get(f'{API_URL}/sdapi/v1/sd-models')
    models = response.json()
    print("Modelli Disponibili:")
    for model in models:
        print(f"- {model['title']}")
    return models

# 2. Impostare il modello desiderato
def set_model(model_title):
    options_payload = {
        "sd_model_checkpoint": model_title
    }
    response = requests.post(
        url=f'{API_URL}/sdapi/v1/options',
        json=options_payload
    )
    if response.status_code == 200:
        print(f"Modello impostato su: {model_title}")
    else:
        print("Errore nell'impostare il modello.")
        print(response.text)

# 3. Effettuare l'inpainting
def perform_inpainting(
    init_image_path,
    mask_image_path,
    prompt,
    negative_prompt,
    output_image_path,
    **kwargs
):
    # Carica e codifica le immagini senza prefisso
    init_image = load_image_base64(init_image_path)
    mask_image = load_image_base64(mask_image_path)

    # Parametri di default per l'inpainting conformi allo schema
    payload = {
        "prompt": prompt,
        "negative_prompt": negative_prompt,
        "styles": [],  # Array di stringhe
        "seed": -1,
        "subseed": -1,
        "subseed_strength": 0.0,
        "seed_resize_from_h": -1,
        "seed_resize_from_w": -1,
        # "sampler_name": None,  # Rimosso per evitare conflitti
        #"scheduler": None,     # Se necessario, altrimenti rimuovere
        "batch_size": 1,
        "n_iter": 1,
        "steps": 100,
        "cfg_scale": 7.0,
        "width": 512,
        "height": 512,
        "restore_faces": False,
        "tiling": False,
        "do_not_save_samples": False,
        "do_not_save_grid": False,
        "eta": 0.0,
        "denoising_strength": 0.75,
        "s_min_uncond": 0.0,
        "s_churn": 0.0,
        "s_tmax": 0.0,
        "s_tmin": 0.0,
        "s_noise": 1.0,
        "override_settings": {},
        "override_settings_restore_afterwards": True,
        "init_images": [init_image],
        "resize_mode": 0,
        "mask": mask_image,
        "mask_blur_x": 4,
        "mask_blur_y": 4,
        "mask_blur": 4,  # Se desideri impostare un valore specifico
        "mask_round": True,
        "inpainting_fill": 1,
        "inpaint_full_res": True,
        "inpaint_full_res_padding": 0,
        "inpainting_mask_invert": 0,
        "initial_noise_multiplier": 1.0,
        "sampler_index": "Euler a",  # Specifica il campionatore
        "include_init_images": False,
        # "script_name": None,  # Rimosso poiché non necessario
        "script_args": [],
        "send_images": True,
        "save_images": False,
        "alwayson_scripts": {},
        "infotext": ""
    }

    # Aggiorna il payload con eventuali parametri aggiuntivi forniti
    payload.update(kwargs)

    # Rimuovi chiavi con valori None per evitare conflitti con l'API
    payload = {k: v for k, v in payload.items() if v is not None}

    # Invio della richiesta
    response = requests.post(
        url=f"{API_URL}/sdapi/v1/img2img",
        headers={"Content-Type": "application/json"},
        json=payload  # Usa 'json' invece di 'data' per inviare JSON
    )

    # Gestione della risposta
    if response.status_code == 200:
        result = response.json()
        image_data = result["images"][0]
        # Decodifica l'immagine senza bisogno di rimuovere il prefisso
        image = base64.b64decode(image_data)
        # Salva l'immagine
        with open(output_image_path, "wb") as f:
            f.write(image)
        print(f"Immagine salvata come {output_image_path}")
    else:
        print("Errore nella richiesta:")
        print(response.status_code)
        print(response.text)


# Esecuzione dello script
if __name__ == "__main__":
    # 1. Ottenere e stampare i modelli disponibili
    models = get_available_models()

    if not models:
        print("Nessun modello disponibile.")
        exit(1)

    # 2. Seleziona il modello desiderato (modifica secondo le tue esigenze)
    # Ad esempio, scegliamo il primo modello nella lista
    selected_model = models[0]['title']
    set_model(selected_model)

    # 3. Definisci i parametri per l'inpainting
    init_image_path = "output_images/source_images/0.png"
    mask_image_path = "output_images/mask_images/0.png"
    prompt = "(White-painted metal surface with realistic scratches:1.5), (scratches revealing underlying bare metal:15), (aged and worn paint with chipping and peeling:1.2), (highly detailed texture with fine imperfections:1.0), photorealistic, ultra high resolution, sharp focus, realistic lighting, metallic sheen, macro photography"
    negative_prompt = "(blurry), (low quality), (distortions), (unnatural colors), (non-metal elements), (concept art), (abstract), (digital artifacts), (overexposed), (underexposed), (noise), (grainy), (low resolution), (watermark), (text), (people), (animals)"
    output_image_path = "output_images/generated_images/0.png"

    # Parametri aggiuntivi conformi allo schema
    inpainting_parameters = {
        "styles": [],
        "seed": -1,
        "subseed": -1,
        "subseed_strength": 0.0,
        "seed_resize_from_h": -1,
        "seed_resize_from_w": -1,
        # "sampler_name": None,  # Rimosso
        "scheduler": None,  # Se non utilizzato, può essere rimosso
        "batch_size": 1,
        "n_iter": 1,
        "steps": 100,
        "cfg_scale": 7.0,
        "width": 512,
        "height": 512,
        "restore_faces": False,
        "tiling": False,
        "do_not_save_samples": False,
        "do_not_save_grid": False,
        "eta": 0.0,
        "denoising_strength": 0.75,
        "s_min_uncond": 0.0,
        "s_churn": 0.0,
        "s_tmax": 0.0,
        "s_tmin": 0.0,
        "s_noise": 1.0,
        "override_settings": {},
        "override_settings_restore_afterwards": True,
        "resize_mode": 0,
        "mask_blur_x": 4,
        "mask_blur_y": 4,
        "mask_blur": 4,
        "mask_round": True,
        "inpainting_fill": 0,
        "inpaint_full_res": True,
        "inpaint_full_res_padding": 32,
        "inpainting_mask_invert": 0,
        "initial_noise_multiplier": 1.0,
        "sampler_index": "Euler a",
        "include_init_images": False,
        # "script_name": None,  # Rimosso
        "script_args": [],
        "send_images": True,
        "save_images": False,
        "alwayson_scripts": {},
        "infotext": ""
    }

    # Rimuovi eventuali parametri con valore None
    inpainting_parameters = {k: v for k, v in inpainting_parameters.items() if v is not None}

    # 4. Effettua l'inpainting con i parametri definiti
    perform_inpainting(
        init_image_path,
        mask_image_path,
        prompt,
        negative_prompt,
        output_image_path,
        **inpainting_parameters
    )
