import os
from typing import List, Any, Dict

from anomaly_generator import get_available_models, set_model, perform_inpainting
from mask_generator import generate_elliptical_mask

# 1. Ottenere e stampare i modelli disponibili
models = get_available_models()

if not models:
    print("Nessun modello disponibile.")
    exit(1)

# 2. Seleziona il modello desiderato (modifica secondo le tue esigenze)
# Ad esempio, scegliamo il primo modello nella lista
selected_model = models[0]['title']
set_model(selected_model)


def generate_anomaly(input_images: str | List[str],
                     mask_parameters: Dict[str, Any] = None,
                     anomaly_kwargs: Dict[str, Any] = None):

    if isinstance(input_images, str):
        input_images = [f"{input_images}/{image_file_name}" for image_file_name in os.listdir(input_images)]

    mask_parameters = mask_parameters if mask_parameters else {}
    anomaly_kwargs = anomaly_kwargs if anomaly_kwargs else {}

    for index, input_image in enumerate(input_images):

        default_mask_parameters = {
            "input_image_path": input_image,
            "output_image_path": f'output_images/source_images/{index}.png',
            "output_mask_path" : f'output_images/mask_images/{index}.png',
            "scaling_factor": 0.1,         # Opzionale
            "eccentricity": None,          # Opzionale
            "center_x": None,              # Opzionale
            "center_y": None,              # Opzionale
            "angle": None,                 # Opzionale
            "allow_out_of_bounds": False,  # Consenti o meno la fuoriuscita dai bordi
            "retry_on_failure": True,      # Opzionale
            "max_attempts": 100            # Opzionale
            }

        print(default_mask_parameters)

        default_mask_parameters.update(mask_parameters)

        print(default_mask_parameters)

        updated_mask_parameters = default_mask_parameters

        generate_elliptical_mask(**updated_mask_parameters)

        # 3. Definisci i parametri per l'inpainting
        init_image_path = f"output_images/source_images/{index}.png"
        mask_image_path = f"output_images/mask_images/{index}.png"

        default_anomaly_kwargs = {
            "White-painted metal surface with realistic scratches": 1.5,
            "scratches revealing underlying bare metal": 15,
            "aged and worn paint with chipping and peeling": 1.2,
            "highly detailed texture with fine imperfections": 1
        }

        default_anomaly_kwargs.update(anomaly_kwargs)
        updated_anomaly_kwargs = default_anomaly_kwargs

        prompt = (f"(White-painted metal surface with realistic scratches:{updated_anomaly_kwargs['White-painted metal surface with realistic scratches']}), "
                  f"(scratches revealing underlying bare metal:{updated_anomaly_kwargs['scratches revealing underlying bare metal']}), "
                  f"(aged and worn paint with chipping and peeling:{updated_anomaly_kwargs['aged and worn paint with chipping and peeling']}), "
                  f"(highly detailed texture with fine imperfections:{updated_anomaly_kwargs['highly detailed texture with fine imperfections']}), "
                  f"photorealistic, ultra high resolution, sharp focus, realistic lighting, metallic sheen, macro photography")

        negative_prompt = "(blurry), (low quality), (distortions), (unnatural colors), (non-metal elements), (concept art), (abstract), (digital artifacts), (overexposed), (underexposed), (noise), (grainy), (low resolution), (watermark), (text), (people), (animals)"

        output_image_path = f"output_images/generated_images/{index}.png"

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


if __name__ == "__main__":

    #input_images = ["input_images/1.png",
    #                "input_images/2.png",
    #                "input_images/3.png",
    #                "input_images/4.png",
    #                "input_images/5.png",
    #                "input_images/6.png",
    #                "input_images/7.png"]

    input_images = "input_images"

    mask_parameters = {
        "scaling_factor": 0.1,  # Opzionale
        "eccentricity": None,  # Opzionale
        "center_x": None,  # Opzionale
        "center_y": None,  # Opzionale
        "angle": None,  # Opzionale
        "allow_out_of_bounds": False,  # Consenti o meno la fuoriuscita dai bordi
        "retry_on_failure": True,  # Opzionale
        "max_attempts": 100  # Opzionale
    }

    anomaly_kwargs = {
        "White-painted metal surface with realistic scratches": 1.5,
        "scratches revealing underlying bare metal": 15,
        "aged and worn paint with chipping and peeling": 1.2,
        "highly detailed texture with fine imperfections": 1
    }

    generate_anomaly(input_images,
                     mask_parameters,
                     anomaly_kwargs)
