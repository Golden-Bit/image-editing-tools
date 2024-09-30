import cv2
import numpy as np
import random
import shutil

def generate_elliptical_mask(input_image_path, output_image_path, output_mask_path,
                             scaling_factor=None, eccentricity=None, center_x=None, center_y=None, angle=None,
                             allow_out_of_bounds=True, retry_on_failure=True, max_attempts=10):
    """
    Genera una maschera ellittica binaria e salva l'immagine originale.

    Parametri:
    - input_image_path (str): Percorso dell'immagine di input.
    - output_image_path (str): Percorso per salvare l'immagine originale.
    - output_mask_path (str): Percorso per salvare la maschera binaria.
    - scaling_factor (float): Fattore di scala per la dimensione dell'ellisse (0.1-1.0). Se None, viene generato casualmente.
    - eccentricity (float): Eccentricità dell'ellisse (0-0.99). Se None, viene generato casualmente.
    - center_x (int): Coordinata X del centro dell'ellisse. Se None, viene generato casualmente.
    - center_y (int): Coordinata Y del centro dell'ellisse. Se None, viene generato casualmente.
    - angle (float): Angolo di orientamento dell'ellisse in gradi (0-360). Se None, viene generato casualmente.
    - allow_out_of_bounds (bool): Se True, permette alla maschera di fuoriuscire dai bordi dell'immagine.
      Se False, assicura che la maschera sia completamente all'interno dei bordi.
    - retry_on_failure (bool): Se True e allow_out_of_bounds è False, riprova con nuovi valori casuali
      se la maschera esce dai bordi dell'immagine.
    - max_attempts (int): Numero massimo di tentativi per generare una maschera valida all'interno dei bordi.
    """
    # Leggi l'immagine di input
    image = cv2.imread(input_image_path)
    if image is None:
        raise ValueError('Errore: impossibile leggere l\'immagine di input.')
    height, width = image.shape[:2]

    # Determina quali parametri sono stati specificati
    center_x_specified = center_x is not None
    center_y_specified = center_y is not None
    scaling_factor_specified = scaling_factor is not None
    eccentricity_specified = eccentricity is not None
    angle_specified = angle is not None

    # Se allow_out_of_bounds è True, procedi senza controllare i bordi
    if allow_out_of_bounds:
        # Genera parametri casuali per quelli non specificati
        if not center_x_specified:
            cx = random.randint(0, width - 1)
        else:
            cx = int(center_x)
        if not center_y_specified:
            cy = random.randint(0, height - 1)
        else:
            cy = int(center_y)
        center = (cx, cy)

        if not scaling_factor_specified:
            s = random.uniform(0.1, 1.0)
        else:
            s = scaling_factor

        if not eccentricity_specified:
            e = random.uniform(0.0, 0.99)
        else:
            e = eccentricity

        if not angle_specified:
            angle_deg = random.uniform(0, 360)
        else:
            angle_deg = angle
        angle_deg = angle_deg % 360

        # Calcola le lunghezze degli assi
        a = int(s * min(width, height) / 2)  # Semi-asse maggiore
        b = int(a * np.sqrt(1 - e ** 2))     # Semi-asse minore
        axes = (a, b)

        # Crea un'immagine nera per la maschera
        mask = np.zeros((height, width), dtype=np.uint8)

        # Disegna l'ellisse bianca sulla maschera
        cv2.ellipse(mask, (cx, cy), axes, angle_deg, 0, 360, 255, -1)

    else:
        # allow_out_of_bounds è False; assicurati che l'ellisse sia completamente all'interno dell'immagine
        attempt = 0
        while attempt < max_attempts:
            attempt += 1

            # Genera parametri casuali per quelli non specificati
            if not center_x_specified:
                cx = random.randint(0, width - 1)
            else:
                cx = int(center_x)
            if not center_y_specified:
                cy = random.randint(0, height - 1)
            else:
                cy = int(center_y)
            center = (cx, cy)

            if not scaling_factor_specified:
                s = random.uniform(0.1, 1.0)
            else:
                s = scaling_factor

            if not eccentricity_specified:
                e = random.uniform(0.0, 0.99)
            else:
                e = eccentricity

            if not angle_specified:
                angle_deg = random.uniform(0, 360)
            else:
                angle_deg = angle
            angle_deg = angle_deg % 360

            # Calcola le lunghezze degli assi
            a = int(s * min(width, height) / 2)  # Semi-asse maggiore
            b = int(a * np.sqrt(1 - e ** 2))     # Semi-asse minore
            axes = (a, b)

            # Verifica che gli assi siano maggiori di zero
            if a <= 0 or b <= 0:
                continue  # Riprova

            # Genera i punti dell'ellisse
            pts = cv2.ellipse2Poly(center=(cx, cy), axes=axes, angle=int(angle_deg), arcStart=0, arcEnd=360, delta=5)

            # Verifica che tutti i punti siano all'interno dell'immagine
            if (pts[:, 0] >= 0).all() and (pts[:, 0] < width).all() and (pts[:, 1] >= 0).all() and (pts[:, 1] < height).all():
                # L'ellisse è completamente all'interno dell'immagine
                # Crea un'immagine nera per la maschera
                mask = np.zeros((height, width), dtype=np.uint8)

                # Disegna l'ellisse bianca sulla maschera
                cv2.ellipse(mask, (cx, cy), axes, angle_deg, 0, 360, 255, -1)
                break
            else:
                if not retry_on_failure:
                    raise ValueError('Errore: la maschera fuoriesce dai bordi dell\'immagine.')
                else:
                    # Se tutti i parametri sono specificati, non possiamo cambiarli
                    if center_x_specified and center_y_specified and scaling_factor_specified and eccentricity_specified and angle_specified:
                        raise ValueError('Errore: la maschera fuoriesce dai bordi dell\'immagine con i parametri specificati.')
                    else:
                        continue  # Riprova
        else:
            # Numero massimo di tentativi raggiunto
            raise ValueError('Errore: impossibile generare una maschera valida entro il numero massimo di tentativi.')

    # Salva l'immagine della maschera
    cv2.imwrite(output_mask_path, mask)

    # Salva l'immagine originale nel percorso di output
    if input_image_path != output_image_path:
        shutil.copy(input_image_path, output_image_path)
    else:
        # Se il percorso di input e output sono uguali, non fare nulla per evitare di sovrascrivere
        pass

if __name__ == "__main__":

    generate_elliptical_mask(
        input_image_path='input_images/0.png',
        output_image_path='output_images/source_images/0.png',
        output_mask_path='output_images/mask_images/0.png',
        scaling_factor=0.1,         # Opzionale
        #eccentricity=0.3,          # Opzionale
        #center_x=100,              # Opzionale
        #center_y=150,              # Opzionale
        #angle=45,                  # Opzionale
        allow_out_of_bounds=False,  # Consenti o meno la fuoriuscita dai bordi
        retry_on_failure=True,      # Opzionale
        max_attempts=999999999      # Opzionale
    )