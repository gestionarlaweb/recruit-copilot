import os
import json
import google.generativeai as genai
from dotenv import load_dotenv
import time
from google.api_core.exceptions import ResourceExhausted

load_dotenv()

import time
from google.api_core.exceptions import ResourceExhausted

def generar_amb_reintents(model, prompt_o_contents, max_intents=3, espera_inicial=4):
    """
    Realitza una crida a Gemini amb reintents automàtics si rep un error 429.
    """
    intent = 0
    espera = espera_inicial

    while intent < max_intents:
        try:
            # Crida al model de Gemini
            response = model.generate_content(prompt_o_contents)
            return response
        except Exception as e:
            # Comprovem si és un error 429 (Quota superada)
            if "429" in str(e) or isinstance(e, ResourceExhausted):
                intent += 1
                if intent >= max_intents:
                    raise RuntimeError(f"S'han esgotat els {max_intents} intents per quota superada (429): {e}")
                
                print(f"⚠️ Avís: Límit de quota superat (429). Reintentant en {espera} segons (Intent {intent}/{max_intents})...")
                time.sleep(espera)
                espera *= 2  # Dupliquem el temps d'espera (Backoff exponencial: 4s, 8s, 16s...)
            else:
                # Si és un altre tipus d'error (ex. clau invàlida, error 400), el llança directament
                raise e

def configure_gemini():
    """Configura el client de Google Generative AI amb la clau d'entorn."""
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("No s'ha trobat la variable d'entorn GEMINI_API_KEY.")
    genai.configure(api_key=api_key)

def get_available_models() -> list:
    """Retorna la llista de models Flash estables optimitzats per a JSON."""
    return [
        "gemini-3.5-flash",
        "gemini-2.5-flash",
        "gemini-3.6-flash",
        "gemini-3.7-flash",
        "gemini-3.8-flash"
    ]

def analyze_cv_with_gemini(cv_text: str, job_description: str, model_name: str = "gemini-3.5-flash") -> dict:
    """
    Analitza un currículum respecte a una oferta de feina utilitzant l'API de Gemini
    amb el model especificat per paràmetre.
    """
    configure_gemini()
    
    prompt = f"""
    Ets un expert sènior en Recursos Humans i selecció de personal industrial i tecnològic. 
    Analitza el següent Currículum respecte a l'oferta de feina proporcionada.
    
    OFERTA DE FEINA:
    {job_description}
    
    CURRÍCULUM DEL CANDIDAT:
    {cv_text}
    
    Retorna la resposta estrictament en format JSON amb les següents claus exactes:
    - "nom": Nom del candidat (o "Desconegut" si no es troba)
    - "puntuacio": Un nombre enter del 0 al 10 segons l'encaix general amb l'oferta
    - "punts_forts": Resum breu de 2 línies dels punts forts respecte al lloc
    - "alertes": Possibles bretxes (ex: falta d'experiència en alguna tecnologia clau, ubicació, disponibilitat)
    - "resum_fitxa": Veredicte ràpid i professional per a l'entrevistador de RRHH
    """
    
    try:
        model = genai.GenerativeModel(
            model_name=model_name,
            generation_config={"response_mime_type": "application/json"}
        )
        response = model.generate_content(prompt)
        return json.loads(response.text)
    except Exception as e:
        return {
            "nom": "Error en analitzar",
            "puntuacio": 0,
            "punts_forts": "N/A",
            "alertes": f"S'ha produït un error tècnic amb el model {model_name}: {str(e)}",
            "resum_fitxa": "No s'ha pogut completar l'anàlisi automàtica."
        }