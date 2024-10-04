from PIL import Image
import os
import shutil

def estrai_tasselli(immagine_input, output_dir, tassello_dim, passo, input_resize=None, output_resize=None,
                    input_rotate=None, output_rotate=None):
    """
    Estrae tasselli di dimensione tassello_dim (NxM) dall'immagine fornita, con passi orizzontale e verticale.

    :param immagine_input: Percorso all'immagine di input.
    :param output_dir: Cartella dove salvare i tasselli estratti.
    :param tassello_dim: Tuple (N, M) che rappresenta la dimensione dei tasselli (larghezza x altezza).
    :param passo: Tuple (Po, Pv) per definire il passo orizzontale e verticale.
    :param input_resize: Tuple opzionale per ridimensionare l'immagine di input (larghezza, altezza). Se None, non ridimensiona.
    :param output_resize: Tuple opzionale per ridimensionare i tasselli estratti (larghezza, altezza). Se None, non ridimensiona.
    :param input_rotate: Gradi per la rotazione in senso orario dell'immagine di input (opzionale).
    :param output_rotate: Gradi per la rotazione in senso orario dei tasselli estratti (opzionale).
    """
    # Carica l'immagine
    immagine = Image.open(immagine_input)

    # Ridimensiona l'immagine di input se specificato
    if input_resize:
        immagine = immagine.resize(input_resize)

    # Ruota l'immagine di input se specificato
    if input_rotate:
        immagine = immagine.rotate(-input_rotate)  # Rotazione oraria (negativa per senso orario)

    # Ottieni dimensioni tassello e passi
    tassello_larghezza, tassello_altezza = tassello_dim
    passo_orizzontale, passo_verticale = passo

    # Crea la directory di output se non esiste
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Ottieni dimensioni dell'immagine
    immagine_larghezza, immagine_altezza = immagine.size

    # Variabile per tenere conto del numero di tasselli estratti
    tassello_count = 0

    # Estrazione dei tasselli
    for y in range(0, immagine_altezza - tassello_altezza + 1, passo_verticale):
        for x in range(0, immagine_larghezza - tassello_larghezza + 1, passo_orizzontale):
            # Definisce il box del tassello: (left, upper, right, lower)
            box = (x, y, x + tassello_larghezza, y + tassello_altezza)
            tassello = immagine.crop(box)

            # Ridimensiona il tassello estratto se output_resize è specificato
            if output_resize:
                tassello = tassello.resize(output_resize)

            # Ruota il tassello estratto se output_rotate è specificato
            if output_rotate:
                tassello = tassello.rotate(-output_rotate)  # Rotazione oraria (negativa per senso orario)

            # Salva il tassello nella cartella di output
            tassello_filename = f"tiles_{tassello_count}.png"
            tassello_path = os.path.join(output_dir, tassello_filename)
            tassello.save(tassello_path)
            tassello_count += 1

    print(f"Processo completato! {tassello_count} tasselli salvati in {output_dir}.")


def processa_directory(directory_input, directory_output, tassello_dim, passo, input_resize=None, output_resize=None,
                       input_rotate=None, output_rotate=None):
    """
    Processa tutte le immagini contenute nella directory di input, estraendo tasselli per ciascuna immagine.
    Per ogni immagine, crea una sottocartella nella directory di output con il nome dell'immagine, e salva i tasselli.

    :param directory_input: Directory contenente le immagini di input.
    :param directory_output: Directory dove verranno salvati i tasselli estratti.
    :param tassello_dim: Dimensione dei tasselli (larghezza, altezza).
    :param passo: Passo orizzontale e verticale (Po, Pv).
    :param input_resize: Ridimensionamento dell'immagine di input (opzionale).
    :param output_resize: Ridimensionamento dei tasselli estratti (opzionale).
    :param input_rotate: Rotazione dell'immagine di input in gradi (opzionale).
    :param output_rotate: Rotazione dei tasselli estratti in gradi (opzionale).
    """
    # Ottiene la lista di tutte le immagini nella directory di input
    immagini = [f for f in os.listdir(directory_input) if os.path.isfile(os.path.join(directory_input, f))]

    # Processa ogni immagine
    for immagine in immagini:
        # Ottieni il percorso completo dell'immagine di input
        immagine_input = os.path.join(directory_input, immagine)

        # Estrai il nome del file senza estensione
        nome_immagine = os.path.splitext(immagine)[0]

        # Crea una sottocartella nella directory di output per questa immagine
        sottocartella_output = os.path.join(directory_output, nome_immagine)

        # Applica la funzione estrai_tasselli su ogni immagine
        estrai_tasselli(immagine_input, sottocartella_output, tassello_dim, passo, input_resize, output_resize,
                        input_rotate, output_rotate)


def organize_tiles_by_position(input_dir):
    # Creazione del path per la cartella di output
    output_dir = input_dir.rstrip('/') + '_reverse'

    # Creazione della nuova directory di output
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Itera sulle sottocartelle 'frame_0000', 'frame_0001', etc.
    for frame_folder in sorted(os.listdir(input_dir)):
        frame_folder_path = os.path.join(input_dir, frame_folder)
        if os.path.isdir(frame_folder_path):
            # Itera sulle immagini dei tiles in ogni frame
            for tile_filename in sorted(os.listdir(frame_folder_path)):
                tile_index = tile_filename.split('_')[-1]  # Identifica il numero del tile
                tile_folder_name = f'tile_{tile_index}'
                tile_folder_path = os.path.join(output_dir, tile_folder_name)

                # Creazione della cartella per i tiles se non esiste
                if not os.path.exists(tile_folder_path):
                    os.makedirs(tile_folder_path)

                # Copia l'immagine nella cartella del tile appropriato
                source_path = os.path.join(frame_folder_path, tile_filename)
                destination_path = os.path.join(tile_folder_path, f'{frame_folder}_{tile_filename}')

                shutil.copy(source_path, destination_path)

    print(f"Organizzazione completata. Immagini salvate in: {output_dir}")



if __name__ == "__main__":
    # Esempio di utilizzo
    directory_input = "cartella_di_input/capture_frame_analisi_difetti_cropped_full"
    directory_output = "cartella_di_output/capture_frame_analisi_difetti_cropped_full"
    tassello_dim = (256, 256)  # Tasselli di dimensione 50x50
    passo = (128, 128)  # Passo orizzontale e verticale di 25 pixel
    input_resize = None #(150, 150)  # Ridimensiona l'immagine di input (opzionale)
    output_resize = None #(512, 512)  # Ridimensiona i tasselli estratti (opzionale)
    input_rotate = None #45  # Rotazione in senso orario dell'immagine di input (opzionale)
    output_rotate = None #30  # Rotazione in senso orario dei tasselli estratti (opzionale)

    # Chiamata della funzione per processare tutte le immagini nella directory
    #processa_directory(directory_input, directory_output, tassello_dim, passo, input_resize, output_resize, input_rotate,
    #                   output_rotate)

    organize_tiles_by_position(directory_output)
