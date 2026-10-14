import os
import json
import time
from dotenv import load_dotenv
import google.generativeai as genai
from google.api_core.exceptions import ResourceExhausted

load_dotenv()

def seleccionar_model_idoni(text_cv: str, text_oferta: str) -> str:
    """
    Avalua el volum de text per determinar quin model de Gemini és el més idoni.
    """
    longitud_total = len(text_cv) + len(text_oferta)
    if longitud_total > 35000:
        return "gemini-1.5-pro"
    else:
        return "gemini-3.5-flash"

def generar_amb_reintents(model, prompt_o_contents, max_intents=3, espera_inicial=4, status_callback=None):
    """
    Realitza una crida a Gemini amb reintents automàtics si rep un error 429
    i notifica a la interfície mitjançant el callback.
    """
    intent = 0
    espera = espera_inicial

    while intent < max_intents:
        try:
            response = model.generate_content(prompt_o_contents)
            return response
        except Exception as e:
            if "429" in str(e) or isinstance(e, ResourceExhausted):
                intent += 1
                missatge = f"⚠️ Avís: Límit de quota superat (429). Reintentant en {espera} segons (Intent {intent}/{max_intents})..."
                
                if intent >= max_intents:
                    raise RuntimeError(f"S'han esgotat els {max_intents} intents per quota superada (429): {e}")
                
                # Imprimim a consola i si hi ha callback, l'executem a la web
                print(missatge)
                if status_callback:
                    status_callback(missatge)
                    
                time.sleep(espera)
                espera *= 2
            else:
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

def analyze_cv_with_gemini(cv_text: str, job_description: str, model_name: str = "gemini-3.5-flash", status_callback=None) -> dict:
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
        
        # Passem el callback cap a la funció de reintents
        response = generar_amb_reintents(model, prompt, status_callback=status_callback)
        
        return json.loads(response.text)
    except Exception as e:
        return {
            "nom": "Error en analitzar",
            "puntuacio": 0,
            "punts_forts": "N/A",
            "alertes": f"S'ha produït un error tècnic amb el model {model_name}: {str(e)}",
            "resum_fitxa": "No s'ha pogut completar l'anàlisi automàtica."
        }