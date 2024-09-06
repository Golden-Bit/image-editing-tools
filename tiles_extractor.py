from PIL import Image
import os


def estrai_tasselli(immagine_input, output_dir, tassello_dim, passo, input_resize=None, output_resize=None):
    """
    Estrae tasselli di dimensione tassello_dim (NxM) dall'immagine fornita, con passi orizzontale e verticale.

    :param immagine_input: Percorso all'immagine di input.
    :param output_dir: Cartella dove salvare i tasselli estratti.
    :param tassello_dim: Tuple (N, M) che rappresenta la dimensione dei tasselli (larghezza x altezza).
    :param passo: Tuple (Po, Pv) per definire il passo orizzontale e verticale.
    :param input_resize: Tuple opzionale per ridimensionare l'immagine di input (larghezza, altezza). Se None, non ridimensiona.
    :param output_resize: Tuple opzionale per ridimensionare i tasselli estratti (larghezza, altezza). Se None, non ridimensiona.
    """
    # Carica l'immagine
    immagine = Image.open(immagine_input)

    # Ridimensiona l'immagine di input se specificato
    if input_resize:
        immagine = immagine.resize(input_resize)

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

            # Salva il tassello nella cartella di output
            tassello_filename = f"tassello_{tassello_count}.png"
            tassello_path = os.path.join(output_dir, tassello_filename)
            tassello.save(tassello_path)
            tassello_count += 1

    print(f"Processo completato! {tassello_count} tasselli salvati in {output_dir}.")


# Esempio di utilizzo
immagine_input = "R.png"
output_dir = "cartella_di_output"
tassello_dim = (50, 50)  # Tasselli di dimensione 50x50
passo = (25, 25)  # Passo orizzontale e verticale di 25 pixel
input_resize = (150, 150)  # Ridimensiona l'immagine di input (opzionale)
output_resize = (150, 150)  # Ridimensiona i tasselli estratti (opzionale)

# Chiamata della funzione
estrai_tasselli(immagine_input, output_dir, tassello_dim, passo, input_resize, output_resize)
