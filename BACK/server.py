
import requests
import zipfile
import io

import os
import time


import json

from fastapi import FastAPI, WebSocket,  WebSocketDisconnect
import uvicorn

from utils.pipeline_load_model_ia_vosk import download_vosk_model
from utils.transcri_by_vosk import transcribe_audio, is_wav_format_compatible, init_model_vosk
from utils.convert_Webm_To_Wav import ensure_conversion_folder, convert_audio_to_wav
from utils.detect_emotion_transfo import load_emotion_model_tabularisai, process_emotion_scores, get_top_sentiment

# initialisation et chargement du model de Vosk pour transcription 
#download_vosk_model()
model_vosk = None

# initialisation et chargement du model de tranformation d'émotion
#load_emotion_model()
emotion_pipeline = None

# Initialisation de l'application FastAPI
app = FastAPI()

   
# Charger le modèle et le pipeline d'émotions
emotion_pipeline = load_emotion_model_tabularisai()

# initialisation et chargement du model de Vosk pour transcription 
download_vosk_model()
model_vosk = init_model_vosk(model_path="Model_ia/vosk_transcript/vosk-model-small-fr-0.22")

# Endpoint de test pour vérifier que le serveur fonctionne
@app.get("/")
async def read_root():
    return {"message": "Hello, world!"}

# Endpoint WebSocket de test
@app.websocket("/ws/test")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    await websocket.send_text("Connexion établie !")
    await websocket.close()
    
    
    

# endpoint pour la réception de l'audio
@app.websocket("/ws/audio")
async def websocket_audio(websocket: WebSocket):
    
    
    
    

    await websocket.accept()
    print("Client connecté sur /ws/audio")
    audio_buffer = bytearray()  # Buffer pour accumuler les données audio

    try:
        while True:
            message = await websocket.receive()  # Réception du message
            # Vérifier le type de message reçu
            if "text" in message:
                try:
                    data = json.loads(message["text"])
                except json.JSONDecodeError:
                    data = {}
                # Si le message texte contient l'action "stop-recording", on sort de la boucle
                if data.get("action") == "stop-recording":
                    print("Commande 'stop-recording' reçue.")
                    break
            elif "bytes" in message:
                # Ajout des données binaires dans le buffer
                chunk = message["bytes"]
                audio_buffer.extend(chunk)
                # Préparer l'accusé de réception sous forme d'objet JSON
                ack = {
                    "typeResponse": "alert",
                    "data": {
                        "SizeChunkTotal": len(audio_buffer),
                        "ChunkSize": len(chunk),
                        "message": "Chunk reçu"
                    }
                }
                # Envoyer l'accusé de réception au client sous forme de JSON
                await websocket.send_text(json.dumps(ack))
                
                
    except WebSocketDisconnect:
        print("Client déconnecté du WebSocket.")
    except Exception as e:
        print(f"[Erreur] Problème lors de la réception des données audio : {e}")

    # Une fois la boucle terminée, affichez la taille totale du buffer
    print("Taille totale des données audio reçues :", len(audio_buffer))
    # Vous pouvez par la suite stocker ce buffer ou le passer à l'étape suivante pour le sauvegarder
    # Par exemple, vous pouvez sauvegarder le contenu dans un fichier dans l'étape 3
    
    folder_record_audio_WebM  = "folder_record_sound/folder_record_audio_WebM"
    try:
        if not os.path.exists(folder_record_audio_WebM ):
            os.makedirs(folder_record_audio_WebM )
            print(f"Dossier '{folder_record_audio_WebM }' créé.")
    except Exception as e:
        print(f"[Erreur] Création du dossier '{folder_record_audio_WebM }' échouée : {e}")

    # Générer un nom de fichier unique
    filename = uniformiser_path( os.path.join(folder_record_audio_WebM , f"audio_{int(time.time())}.webm") )
    try:
        with open(filename, "wb") as f:
            f.write(audio_buffer)
        print(f"Fichier audio sauvegardé : {filename}")
        # Optionnel : envoyer au client une confirmation de sauvegarde
        ack = {
            "typeResponse": "data",
            "data": {
                "message": "Fichier audio sauvegardé",
                "filename": filename,
                "totalSize": len(audio_buffer)
            }
        }
        
        print(f"Fichier audio ::  {filename}")
        
        
        
        # 1. Vérifier/Créer le dossier de conversion
        conversion_folder = ensure_conversion_folder()
        if conversion_folder is None:
            print("[Erreur] Impossible d'obtenir le dossier de conversion.")
            
        else:
            original_file = filename
            # 2. Définir le nom du fichier WAV converti (en se basant sur l'original)
            # Ici, on retire l'extension .webm et on ajoute .wav
            base_name = os.path.splitext(os.path.basename(original_file))[0]
            wav_file = uniformiser_path ( os.path.join(conversion_folder, f"{base_name}.wav") )
            
            # 0. init vosk 
            global model_vosk
            
            # 3. Convertir le fichier WebM en WAV
            if convert_audio_to_wav(original_file, wav_file):
                # 4. Lancer la transcription
                transcription = transcribe_audio(wav_file, model_vosk)
                #transcription = "joel te test hein"
                print("Transcription :", transcription)
                
                
                # 0. init instance detect emotion
                global emotion_pipeline
                
                #sample_text = "Je ne pense pas etre satisfais du service , passez une meilleur journee"
                
                
                
                
                
                
                print (f"emotion_pipeline dans le process ::  {emotion_pipeline}")
                
                output = emotion_pipeline(transcription)
                final_result = process_emotion_scores(output)
                #print("\n\nRésultat de l'analyse brute sur le texte sample :")
                #print(final_result)
                final_data_score = final_result["data"]
                
                ack = {
                        "typeResponse": "resultSensationScan",
                        "data": final_data_score,
                        "top_sensation" : get_top_sentiment(final_data_score)
                    }
                print(f"------- Data ::: >>  {ack}-------")
                await websocket.send_text(json.dumps(ack))
                
            else:
                print("[Erreur] La conversion du fichier audio a échoué.")
                ack = {
                        "typeResponse": "alert",
                        "data": {
                            "message": "Erreur lors de convert_audio_to_wav ",
                        }
                    }
                await websocket.send_text(json.dumps(ack))
                
                
                
                
                
        
        #await websocket.send_text(json.dumps(ack))
    except Exception as e:
        print(f"[Erreur] Impossible de sauvegarder le fichier audio : {e}")
        ack = {
            "typeResponse": "alert",
            "data": {
                "message": "Erreur lors de la sauvegarde du fichier audio enregistrer ",
                "error": str(e)
            }
        }
        await websocket.send_text(json.dumps(ack))
    
    
    
    
    




def uniformiser_path(path: str) -> str:
    """
    Uniformise le chemin d'accès en utilisant le séparateur de dossiers adapté au système.
    
    Exemple :
      uniformiser_path("folder_record_sound/folder_record_audio_WebM\\audio_1738461552.webm")
      uniformiser_path("folder_record_sound/folder_record_audio_WebM/audio_1738461552.webm")
    
    Retourne un chemin cohérent.
    """
    return os.path.normpath(path)
        


# Lancement du serveur via uvicorn
if __name__ == "__main__":
    

    # initialisation et chargement du model de tranformation d'émotion
    #load_emotion_model()
    #load_emotion_model_tabularisai()
    
 
    
    print (f"emotion_pipeline ::  {emotion_pipeline}")
    
    # Si le modèle a été chargé, testez-le sur un autre texte
    if emotion_pipeline:
        sample_text = "Je ne pense pas etre satisfais du service , passez une meilleur journee"
        output = emotion_pipeline(sample_text)
        final_result = process_emotion_scores(output)
        print("\n\nRésultat de l'analyse brute sur le texte sample :")
        print(output)
        
        print(f"\n\nRésultat des emotion :")
        print(final_result)
    
    
    
    uvicorn.run("server:app", host="127.0.0.1", port=8000, reload=True)
