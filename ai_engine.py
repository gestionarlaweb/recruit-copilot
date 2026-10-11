import os
import json
import google.generativeai as genai
from dotenv import load_dotenv

# Càrrega automàtica del fitxer .env local
load_dotenv()

def configure_gemini():
    """Configura el client de Google Generative AI amb la clau d'entorn."""
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("No s'ha trobat la variable d'entorn GEMINI_API_KEY.")
    genai.configure(api_key=api_key)

def analyze_cv_with_gemini(cv_text: str, job_description: str) -> dict:
    """
    Analitza un currículum respecte a una oferta de feina utilitzant l'API de Gemini.
    Retorna un diccionari amb les dades estructurades de l'avaluació.
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
    
    model = genai.GenerativeModel(
        model_name="gemini-3.5-flash",
        generation_config={"response_mime_type": "application/json"}
    )
    
    try:
        response = model.generate_content(prompt)
        return json.loads(response.text)
    except Exception as e:
        return {
            "nom": "Error en analitzar",
            "puntuacio": 0,
            "punts_forts": "N/A",
            "alertes": f"S'ha produït un error tècnic processant aquest CV: {str(e)}",
            "resum_fitxa": "No s'ha pogut completar l'anàlisi automàtica."
        }