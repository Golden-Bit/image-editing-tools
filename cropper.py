import os
from PIL import Image

def verifica_coerenza(directory_input, directory_maschere):
    """
    Verifica che il numero di immagini e maschere corrisponda e che ogni immagine abbia una maschera con lo stesso nome.
    """
    immagini = sorted([f for f in os.listdir(directory_input) if os.path.isfile(os.path.join(directory_input, f))])
    maschere = sorted([f for f in os.listdir(directory_maschere) if os.path.isfile(os.path.join(directory_maschere, f))])

    if len(maschere) > 1 and len(immagini) != len(maschere):
        raise ValueError(f"Il numero di immagini ({len(immagini)}) e maschere ({len(maschere)}) non corrisponde.")

    return immagini, maschere


def crop_con_maschera(immagine_input, maschera_input, output_path, resize_maschera=False):
    """
    Applica la maschera a un'immagine e salva il risultato.

    :param immagine_input: Percorso dell'immagine di input.
    :param maschera_input: Percorso della maschera in bianco e nero.
    :param output_path: Percorso dove salvare l'immagine risultante.
    :param resize_maschera: Se True, ridimensiona la maschera per adattarla all'immagine di input.
    """
    # Carica l'immagine
    immagine = Image.open(immagine_input).convert('RGBA')
    maschera = Image.open(maschera_input).convert('L')  # La maschera deve essere in scala di grigi (L)

    # Ottieni le dimensioni dell'immagine
    immagine_larghezza, immagine_altezza = immagine.size

    # Ridimensiona la maschera se necessario
    if resize_maschera and maschera.size != immagine.size:
        maschera = maschera.resize((immagine_larghezza, immagine_altezza))

    # Trova il bounding box della maschera (area dei pixel bianchi)
    bbox = maschera.getbbox()

    if bbox:
        # Ritaglia l'immagine utilizzando il bounding box
        immagine_ritagliata = immagine.crop(bbox)

        # Salva l'immagine ritagliata
        immagine_ritagliata.save(output_path)
        print(f"Immagine ritagliata salvata in: {output_path}")
    else:
        print(f"Nessun pixel bianco nella maschera per l'immagine {os.path.basename(immagine_input)}. Nessun ritaglio eseguito.")


def processa_directory_con_maschere(directory_input, directory_maschere, directory_output, resize_maschera=False):
    """
    Applica una maschera di cropping a tutte le immagini nella directory di input.
    Se c'è una sola maschera nella directory delle maschere, viene applicata a tutte le immagini.
    Se ci sono più maschere, vengono associate per nome alle immagini.

    :param directory_input: Directory contenente le immagini di input.
    :param directory_maschere: Directory contenente le maschere.
    :param directory_output: Directory dove salvare le immagini croppate.
    :param resize_maschera: Se True, ridimensiona la maschera per adattarla all'immagine di input.
    """
    # Ottieni le liste delle immagini e delle maschere
    immagini = sorted([f for f in os.listdir(directory_input) if os.path.isfile(os.path.join(directory_input, f))])
    maschere = sorted([f for f in os.listdir(directory_maschere) if os.path.isfile(os.path.join(directory_maschere, f))])

    # Se c'è una sola maschera, applicala a tutte le immagini
    if len(maschere) == 1:
        unica_maschera = os.path.join(directory_maschere, maschere[0])
        for immagine in immagini:
            immagine_input = os.path.join(directory_input, immagine)
            output_path = os.path.join(directory_output, immagine)

            # Crea la directory di output se non esiste
            if not os.path.exists(directory_output):
                os.makedirs(directory_output)

            # Applica la maschera di cropping all'immagine
            crop_con_maschera(immagine_input, unica_maschera, output_path, resize_maschera)

    # Se ci sono più maschere, verifica coerenza e applica associazione per nome
    else:
        immagini, maschere = verifica_coerenza(directory_input, directory_maschere)

        # Processa ogni coppia di immagine e maschera
        for immagine, maschera in zip(immagini, maschere):
            # Percorso completo dell'immagine e della maschera
            immagine_input = os.path.join(directory_input, immagine)
            maschera_input = os.path.join(directory_maschere, maschera)

            # Percorso completo dell'immagine di output
            output_path = os.path.join(directory_output, immagine)

            # Crea la directory di output se non esiste
            if not os.path.exists(directory_output):
                os.makedirs(directory_output)

            # Applica la maschera di cropping all'immagine
            crop_con_maschera(immagine_input, maschera_input, output_path, resize_maschera)


if __name__ == "__main__":

    # Esempio di utilizzo
    directory_input = "cartella_di_input/capture_frame_analisi_difetti"
    directory_maschere = "masks"
    directory_output = "cartella_di_output/capture_frame_analisi_difetti_cropped_full"
    resize_maschera = True  # Ridimensiona la maschera se necessario

    # Chiamata della funzione per processare tutte le immagini e maschere corrispondenti
    processa_directory_con_maschere(directory_input, directory_maschere, directory_output, resize_maschera)

