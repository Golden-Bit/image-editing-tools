import os
import random
from PIL import Image, ImageDraw, ImageOps

def genera_maschera_ellittica(image_size, bbox_size_range, rotazione_range, output_dir, num_maschere=1):
    """
    Genera una maschera con un'ellisse bianca su sfondo nero, adattata a un bounding box e con possibilità di rotazione.

    :param image_size: Tuple (larghezza, altezza) delle dimensioni dell'immagine di output.
    :param bbox_size_range: Tuple ((min_larghezza, max_larghezza), (min_altezza, max_altezza)) che definisce il range di dimensioni del bounding box.
    :param rotazione_range: Tuple (min_rotazione, max_rotazione) che definisce il range di gradi per la rotazione.
    :param output_dir: Directory dove salvare le maschere generate.
    :param num_maschere: Numero di maschere casuali da generare.
    """
    larghezza_img, altezza_img = image_size
    (min_bbox_larghezza, max_bbox_larghezza), (min_bbox_altezza, max_bbox_altezza) = bbox_size_range
    min_rotazione, max_rotazione = rotazione_range

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for i in range(num_maschere):
        while True:
            # Crea un'immagine nera
            maschera = Image.new('L', (larghezza_img, altezza_img), 0)  # L per scala di grigi, 0 = nero
            draw = ImageDraw.Draw(maschera)

            # Seleziona casualmente la dimensione del bounding box
            bbox_larghezza = random.randint(min_bbox_larghezza, max_bbox_larghezza)
            bbox_altezza = random.randint(min_bbox_altezza, max_bbox_altezza)

            # Posizionamento casuale del bounding box che non esce dai bordi
            x1 = random.randint(0, larghezza_img - bbox_larghezza)
            y1 = random.randint(0, altezza_img - bbox_altezza)
            x2 = x1 + bbox_larghezza
            y2 = y1 + bbox_altezza

            # Definisce il bounding box
            bbox = (x1, y1, x2, y2)

            # Disegna l'ellisse bianca che tocca i bordi del bounding box
            draw.ellipse(bbox, fill=255)  # 255 = bianco

            # Seleziona casualmente l'angolo di rotazione
            angolo_rotazione = random.uniform(min_rotazione, max_rotazione)

            # Crea una nuova immagine temporanea per la rotazione
            maschera_rotata = maschera.rotate(angolo_rotazione, expand=True)

            # Trova i bordi dell'immagine ruotata
            bbox_rotata = maschera_rotata.getbbox()

            # Controlla se il bounding box ruotato esce dai bordi dell'immagine originale
            if bbox_rotata[2] <= larghezza_img and bbox_rotata[3] <= altezza_img:
                # Se la rotazione è valida, continua
                maschera = ImageOps.fit(maschera_rotata, (larghezza_img, altezza_img), method=0, centering=(0.5, 0.5))
                break  # Uscita dal ciclo solo se il bounding box ruotato è valido

        # Salva la maschera
        maschera_filename = f"maschera_{i + 1}.png"
        maschera_path = os.path.join(output_dir, maschera_filename)
        maschera.save(maschera_path)
        print(f"Maschera {i + 1} salvata in: {maschera_path}")


# Esempio di utilizzo
if __name__ == "__main__":
    # Parametri dell'immagine di output
    image_size = (400, 400)  # Larghezza x Altezza dell'immagine di output

    # Range di dimensione del bounding box dell'ellisse
    bbox_size_range = ((100, 200), (75, 150))  # Larghezza (min, max), Altezza (min, max)

    # Range di rotazione in gradi (positivo per orario, negativo per antiorario)
    rotazione_range = (-45, 45)  # Rotazione minima e massima

    # Directory di output
    output_dir = "maschere_output"

    # Numero di maschere da generare
    num_maschere = 20

    # Genera maschere
    genera_maschera_ellittica(image_size, bbox_size_range, rotazione_range, output_dir, num_maschere)
