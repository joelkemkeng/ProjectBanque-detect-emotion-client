import subprocess
import os
import wave



import json
from vosk import Model, KaldiRecognizer




def init_model_vosk(model_path="Model_ia/vosk_transcript/vosk-model-small-fr-0.22") :
    """
    Initialise le modèle VOSK pour la transcription d'audio.
    """
    try:
        return Model(model_path)
    except Exception as e:
        print(f"[Erreur] Chargement du modèle VOSK échoué : {e}")
        return None



def transcribe_audio(file_path: str, model_path="Model_ia/vosk_transcript/vosk-model-small-fr-0.22") -> str:
    """
    Transcrit le fichier audio WAV (doit être au format requis) en texte avec VOSK.
    """
    if not is_wav_format_compatible(file_path):
        print(f"[Erreur] Le fichier {file_path} n'est pas au format requis pour VOSK (mono, 16kHz, 16 bits PCM).")
        return ""
    


    try:
        wf = wave.open(file_path, "rb")
    except Exception as e:
        print(f"[Erreur] Impossible d'ouvrir le fichier audio '{file_path}' : {e}")
        return ""
    
    try:
        model = Model(model_path)
    except Exception as e:
        print(f"[Erreur] Chargement du modèle VOSK échoué : {e}")
        wf.close()
        return ""
    
    rec = KaldiRecognizer(model, wf.getframerate())
    rec.SetWords(True)
    result_text = ""
    
    try:
        while True:
            data = wf.readframes(4000)
            if len(data) == 0:
                break
            if rec.AcceptWaveform(data):
                res = json.loads(rec.Result())
                result_text += " " + res.get("text", "")
        final_res = json.loads(rec.FinalResult())
        result_text += " " + final_res.get("text", "")
    except Exception as e:
        print(f"[Erreur] Problème lors de la transcription : {e}")
        wf.close()
        return ""
    
    wf.close()
    return result_text.strip()







def transcribe_audio(file_path,model_charger ) :
    
    
    """
    Transcrit le fichier audio WAV (doit être au format requis) en texte avec VOSK.
    """
    if not is_wav_format_compatible(file_path):
        print(f"[Erreur] Le fichier {file_path} n'est pas au format requis pour VOSK (mono, 16kHz, 16 bits PCM).")
        return ""
    
    try:
        wf = wave.open(file_path, "rb")
    except Exception as e:
        print(f"[Erreur] Impossible d'ouvrir le fichier audio '{file_path}' : {e}")
        return ""
    
    '''
    try:
        model = Model(model_path)
    except Exception as e:
        print(f"[Erreur] Chargement du modèle VOSK échoué : {e}")
        wf.close()
        return ""
        '''
        
        
    if(model_charger == None):
        print("chargement du model Echouer, pendant la Transcription de de audion dans la fonction >> transcribe_audio")
        return ""
    
    rec = KaldiRecognizer(model_charger, wf.getframerate())
    rec.SetWords(True)
    result_text = ""
    
    try:
        while True:
            data = wf.readframes(4000)
            if len(data) == 0:
                break
            if rec.AcceptWaveform(data):
                res = json.loads(rec.Result())
                result_text += " " + res.get("text", "")
        final_res = json.loads(rec.FinalResult())
        result_text += " " + final_res.get("text", "")
    except Exception as e:
        print(f"[Erreur] Problème lors de la transcription : {e}")
        wf.close()
        return ""
    
    wf.close()
    return result_text.strip()




def is_wav_format_compatible(file_path):
    """
    Vérifie que le fichier WAV est en mono, 16 kHz, 16 bits PCM.
    """
    try:
        wf = wave.open(file_path, "rb")
        channels = wf.getnchannels()
        sampwidth = wf.getsampwidth()
        framerate = wf.getframerate()
        wf.close()
        return channels == 1 and sampwidth == 2 and framerate == 16000
    except Exception as e:
        print(f"[Erreur] Vérification du format du fichier WAV a échoué : {e}")
        return False
