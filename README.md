# 🎯 Recruit-Co-pilot: Filtre Intel·ligent de Candidats

Eina de suport per al departament de **Recursos Humans**, dissenyada per automatitzar i agilitzar el garbell i anàlisi inicial de currículums (CVs) mitjançant Intel·ligència Artificial.

## 🚀 Característiques Principals
- **Anàlisi Massiva de PDFs**: Puja un o múltiples currículums en format PDF de manera simultània.
- **Creuament Intel·ligent amb l'Oferta**: Compara automàticament les competències del candidat amb els requisits específics de la plaça.
- **Rànquing Objectiu**: Genera una taula ordenada amb puntuacions del 0 al 10 per a cada candidat.
- **Veredicte per a l'Entrevistador**: Extreu punts forts, possibles bretxes (alertes) i un resum executiu per facilitar la presa de decisions del equip de Personas.

## 🛠️ Stack Tecnològic
- **Llenguatge**: Python 3.11+
- **Interfície Web**: Streamlit
- **Motor d'IA**: Google Gemini API amb resposta estructurada en JSON.
- **Processament de Documents**: PyPDF & Pandas
- **Contenidors**: Docker & Docker Compose

---

## ⚙️ Instal·lació i Execució Local

Segueix aquests passos per configurar i provar l'aplicació a la teva màquina:

### 1. Clonar el repositori
```bash
git clone [https://github.com/tu-usuari/recruit-copilot.git](https://github.com/tu-usuari/recruit-copilot.git)
cd recruit-copilot