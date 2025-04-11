import os
import requests
import zipfile
import io

def download_vosk_model(
    model_dir="Model_ia/vosk_transcript", 
    model_name="vosk-model-small-fr-0.22",
    model_url="https://alphacephei.com/vosk/models/vosk-model-small-fr-0.22.zip"
):
    """
    Vérifie la présence du modèle VOSK pour le français dans model_dir.
    S'il n'existe pas, crée les dossiers et télécharge le modèle depuis model_url.
    """
    # Création récursive du dossier s'il n'existe pas
    if not os.path.exists(model_dir):
        try:
            os.makedirs(model_dir, exist_ok=True)
            print(f"Dossier '{model_dir}' créé.")
        except Exception as e:
            print(f"[Erreur] Création du dossier '{model_dir}' échouée : {e}")
            return False

    model_path = os.path.join(model_dir, model_name)
    if os.path.exists(model_path):
        print(f"Le modèle '{model_name}' existe déjà dans '{model_dir}'.")
        return True
    else:
        print(f"Téléchargement du modèle '{model_name}' depuis {model_url}...")
        try:
            response = requests.get(model_url, stream=True)
            response.raise_for_status()
            # Extraction du zip depuis le contenu en mémoire
            with zipfile.ZipFile(io.BytesIO(response.content)) as z:
                z.extractall(path=model_dir)
            print(f"Modèle téléchargé et extrait dans '{model_dir}'.")
            return True
        except Exception as e:
            print(f"[Erreur] Téléchargement ou extraction du modèle a échoué : {e}")
            return False

# Exemple d'utilisation :
if __name__ == "__main__":
    download_vosk_model()
