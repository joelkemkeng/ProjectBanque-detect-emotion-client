from transformers import pipeline, AutoModelForSequenceClassification, AutoTokenizer
import os




'''

def load_emotion_model(model_dir="Model_ia/emotion_model", 
                       model_name="cardiffnlp/twitter-xlm-roberta-base-emotion"):
    """
    Charge (et télécharge au besoin) le modèle d'émotions dans le dossier indiqué.
    Retourne un pipeline de classification du texte configuré pour retourner tous les scores.
    """
    # Créer le dossier s'il n'existe pas
    if not os.path.exists(model_dir):
        try:
            os.makedirs(model_dir, exist_ok=True)
            print(f"Dossier '{model_dir}' créé pour le modèle d'émotion.")
        except Exception as e:
            print(f"[Erreur] Création du dossier '{model_dir}' échouée : {e}")
            return None
    try:
        tokenizer = AutoTokenizer.from_pretrained(model_name, cache_dir=model_dir)
        model = AutoModelForSequenceClassification.from_pretrained(model_name, cache_dir=model_dir)
        emotion_pipe = pipeline("text-classification", model=model, tokenizer=tokenizer, return_all_scores=True)
        print("Modèle d'émotion chargé avec succès.")
        return emotion_pipe
    except Exception as e:
        print(f"[Erreur] Chargement du modèle d'émotion a échoué : {e}")
        return None





def load_emotion_model_tabularisai(model_dir="Model_ia/emotion_model", 
                       model_name="tabularisai/multilingual-sentiment-analysis"):
    """
    Charge (et télécharge au besoin) le modèle d'émotions dans le dossier indiqué.
    Retourne un pipeline de classification du texte configuré pour retourner tous les scores.
    """
    # Créer le dossier s'il n'existe pas
    if not os.path.exists(model_dir):
        try:
            os.makedirs(model_dir, exist_ok=True)
            print(f"Dossier '{model_dir}' créé pour le modèle d'émotion.")
        except Exception as e:
            print(f"[Erreur] Création du dossier '{model_dir}' échouée : {e}")
            return None
    try:
        
        tokenizer = AutoTokenizer.from_pretrained("tabularisai/multilingual-sentiment-analysis")
        model = AutoModelForSequenceClassification.from_pretrained("tabularisai/multilingual-sentiment-analysis")
        inputs = tokenizer("Hello, my dog is cute", return_tensors="pt")
        emotion_pipe = pipeline("text-classification", model=model, tokenizer=tokenizer, top_k=None)
        print("Modèle d'émotion chargé avec succès.")
        print(f"result: {input}")
        return model
    except Exception as e:
        print(f"[Erreur] Chargement du modèle d'émotion a échoué : {e}")
        return None
'''




def load_emotion_model_tabularisai(model_dir="Model_ia/emotion_model", 
                                   model_name="tabularisai/multilingual-sentiment-analysis"):
    """
    Charge (et télécharge au besoin) le modèle d'émotions dans le dossier indiqué.
    Retourne un pipeline de classification du texte configuré pour retourner tous les scores.
    """
    # Créer le dossier s'il n'existe pas
    if not os.path.exists(model_dir):
        try:
            os.makedirs(model_dir, exist_ok=True)
            print(f"Dossier '{model_dir}' créé pour le modèle d'émotion.")
        except Exception as e:
            print(f"[Erreur] Création du dossier '{model_dir}' échouée : {e}")
            return None
    try:
        # Charger le tokenizer et le modèle depuis Hugging Face en utilisant le cache_dir
        tokenizer = AutoTokenizer.from_pretrained(model_name, cache_dir=model_dir)
        model = AutoModelForSequenceClassification.from_pretrained(model_name, cache_dir=model_dir)
        # Créer le pipeline pour la classification de texte
        emotion_pipe = pipeline("text-classification", model=model, tokenizer=tokenizer, top_k=None)
        print("Modèle d'émotion chargé avec succès.")

        # Tester le pipeline sur un texte d'exemple
        #test_text = "Hello, my dog is cute"
        #result = emotion_pipe(test_text)
        #print(f"Test sur texte d'exemple : {result}")
        
        return emotion_pipe
    except Exception as e:
        print(f"[Erreur] Chargement du modèle d'émotion a échoué : {e}")
        return None
    
    
    
    
def process_emotion_scores(model_response: list) -> dict:
    
    """
    Traite la réponse d'un modèle de sentiment encadrée par deux crochets et retourne un objet JSON
    avec les scores sur 5 pour les émotions suivantes :
        - colère (Very Negative)
        - peur (moyenne de Negative et Very Negative)
        - joie (Positive)
        - amour (Very Positive)
        - tristesse (Negative)
        - surprise (Neutral)

    Exemple d'entrée (model_response) :
        [[
            {'label': 'Neutral', 'score': 0.6664808392524719},
            {'label': 'Very Positive', 'score': 0.21574744582176208},
            {'label': 'Positive', 'score': 0.06731870770454407},
            {'label': 'Very Negative', 'score': 0.029952004551887512},
            {'label': 'Negative', 'score': 0.02050093561410904}
        ]]
        
    La fonction extrait la liste interne et calcule les scores sur 5.
    """
    # Si la réponse est encadrée par deux crochets, on récupère l'inner list.
    if isinstance(model_response, list) and len(model_response) > 0 and isinstance(model_response[0], list):
        model_scores = model_response[0]
    else:
        model_scores = model_response

    # Récupérer les scores par label
    positive = next((item['score'] for item in model_scores if item['label'] == 'Positive'), 0)
    very_positive = next((item['score'] for item in model_scores if item['label'] == 'Very Positive'), 0)
    neutral = next((item['score'] for item in model_scores if item['label'] == 'Neutral'), 0)
    negative = next((item['score'] for item in model_scores if item['label'] == 'Negative'), 0)
    very_negative = next((item['score'] for item in model_scores if item['label'] == 'Very Negative'), 0)

    # Calcul heuristique : conversion sur 5
    joie = round(positive * 5, 2)
    amour = round(very_positive * 5, 2)
    surprise = round(neutral * 5, 2)
    tristesse = round(negative * 5, 2)
    colere = round(very_negative * 5, 2)
    peur = round(((negative + very_negative) / 2) * 5, 2)

    # Construction du résultat final
    result = {
        "colere": colere,
        "peur": peur,
        "joie": joie,
        "amour": amour,
        "tristesse": tristesse,
        "surprise": surprise
    }

    # Affichage des scores dans la console
    print("Scores d'émotions normalisés sur 5 :")
    for emotion, score in result.items():
        print(f"  {emotion} : {score}/5")

    # Retourne l'objet JSON final
    return {"data": result}







def get_top_sentiment(emotion_scores: dict) -> str:
    """
    Retourne le sentiment ayant le plus grand score.
    
    Exemple :
    >>> result = {
    ...     "colere": 1.2,
    ...     "peur": 1.5,
    ...     "joie": 2.1,
    ...     "amour": 2.3,
    ...     "tristesse": 2.8,
    ...     "surprise": 2
    ... }
    >>> print(get_top_sentiment(result))
    tristesse
    """
    if not emotion_scores:
        return ""
    # max retourne la clé ayant la valeur maximale dans le dictionnaire
    top_sentiment = max(emotion_scores, key=emotion_scores.get)
    return top_sentiment

