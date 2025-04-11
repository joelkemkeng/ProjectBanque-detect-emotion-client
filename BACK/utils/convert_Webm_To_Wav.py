import subprocess
import os
import imageio_ffmpeg

def convert_audio_to_wav(input_file, output_file):

    """
    Convertit le fichier audio (par exemple en WebM) en WAV au format optimal pour VOSK :
    - Mono, 16 kHz, 16 bits PCM.
    """
    # Vérification de la présence de ffmpeg --- ici c'est le cas ou on utilise le ffmpeg telecharger manuellement sur windows
    """
    try:
        subprocess.run(["ffmpeg", "-version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
    except Exception as e:
        print(f"[Erreur] ffmpeg n'est pas installé ou non accessible : {e}")
        return False
    """


    if convert_with_imageio_ffmpeg(input_file, output_file) :
        return True
    
    else :
        return False




def convert_with_ffmpeg(input_file, output_file):

    # Commande de conversion
    command = [
        "ffmpeg",
        "-y",                   # Overwrite output file without asking
        "-i", input_file,       # Fichier source
        "-ac", "1",             # Mono
        "-ar", "16000",         # 16 kHz
        "-sample_fmt", "s16",   # 16 bits PCM
        output_file
    ]
    try:
        subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        print(f"Conversion réussie : {input_file} -> {output_file}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"[Erreur] Conversion avec ffmpeg a échoué : {e}")
        return False





def convert_with_imageio_ffmpeg(input_file, output_file):

    """
    Convertit le fichier audio (par exemple en WebM) en WAV au format optimal pour VOSK :
    - Mono, 16 kHz, 16 bits PCM.
    """
    try:
        # Récupérer le chemin du binaire ffmpeg portable pour la plateforme en cours
        ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
    except Exception as e:
        print(f"[Erreur] Impossible de récupérer ffmpeg avec imageio-ffmpeg : {e}")
        return False

    command = [
        ffmpeg_exe,
        "-y",                   # Écrase le fichier de sortie s'il existe
        "-i", input_file,       # Fichier source
        "-ac", "1",             # Convertir en mono
        "-ar", "16000",         # Taux d'échantillonnage à 16 kHz
        "-sample_fmt", "s16",   # Format 16 bits PCM
        output_file
    ]
    try:
        subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        print(f"Conversion réussie : {input_file} -> {output_file}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"[Erreur] La conversion avec ffmpeg a échoué : {e}")
        return False









def ensure_conversion_folder(conversion_folder="folder_record_sound/folder_Convert_Webm_Audio_Wav"):
    """
    Vérifie et crée le dossier de conversion pour sauvegarder les fichiers WAV convertis.
    """
    if not os.path.exists(conversion_folder):
        try:
            os.makedirs(conversion_folder, exist_ok=True)
            print(f"Dossier de conversion '{conversion_folder}' créé.")
        except Exception as e:
            print(f"[Erreur] Création du dossier de conversion '{conversion_folder}' échouée : {e}")
            return None
    return conversion_folder



