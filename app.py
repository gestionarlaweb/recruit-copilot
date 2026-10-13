import streamlit as st
import pandas as pd
from pypdf import PdfReader
from ai_engine import analyze_cv_with_gemini, get_available_models

# Configuració de la pàgina
st.set_page_config(
    page_title="Recruit-Co-pilot",
    page_icon="🎯",
    layout="wide"
)

st.title("🎯 Recruit-Co-pilot: Filtre Intel·ligent de Candidats")
st.markdown("Eina interna de suport per al departament de **Recursos Humans**.")

# --- BARRA LATERAL (Configuració i Oferta) ---
st.sidebar.header("⚙️ Configuració d'IA")

# Advertència visible damunt del desplegable
st.sidebar.warning(
    "⚠️ **Recomanació:** Utilitza **gemini-3.8-flash** a data de 12/10/2026"
    "per garantir una estabilitat total i compatibilitat amb el format JSON."
    "A tenir en compte que els models més nous poden oferir millores, però també poden introduir inestabilitat en la resposta JSON."
)

model_options = get_available_models()

# Seleccionar per defecte "gemini-3.5-flash"
default_index = 0
for idx, model in enumerate(model_options):
    if model == "gemini-3.5-flash":
        default_index = idx
        break

selected_model = st.sidebar.selectbox("Selecciona el Model de Gemini", model_options, index=default_index)

# Barra lateral per a l'oferta de feina
st.sidebar.header("📋 1. Definició de l'Oferta")
default_jd = """Buscant Desenvolupador/a de IA per a Empresa demo.
Missió: Liderar l'automatització de processos de Recursos Humans amb IA generativa, agents i RAG.
Requisits:
- Experiència en desenvolupament full stack (Python, APIs REST, SQL, Git).
- Experiència amb IA generativa (integració d'LLMs, prompts, sistemes RAG, agents).
- Experiència amb Flutter.
- Molt valorable: Tenir algo de coneixement en SpringBoot, Java.
- Idiomes: Català i castellà natiu, anglès tècnic.
- Ubicació: Malgrat de Mar, Girona o rodalies / disponibilitat de desplaçament."""

job_description = st.sidebar.text_area(
    "Requisits i detalls de la plaça:",
    value=default_jd,
    height=300
)

# Secció principal: Pujada de CVs
st.header("📂 2. Càrrega de Currículums")
st.markdown("Puja un o diversos currículums en format **PDF** per iniciar l'anàlisi automatitzada.")

uploaded_files = st.file_uploader(
    "Selecciona els arxius PDF dels candidats",
    type=["pdf"],
    accept_multiple_files=True
)

if uploaded_files and job_description:
    if st.button("🚀 Analitzar i Ordenar Candidats amb IA", type="primary"):
        results = []
        progress_bar = st.progress(0)
        total_files = len(uploaded_files)
        
        status_text = st.empty()
        
        for i, file in enumerate(uploaded_files):
            status_text.text(f"Processant ({i+1}/{total_files}): {file.name} amb el model `{selected_model}`...")
            
            try:
                # Extreure text del PDF
                reader = PdfReader(file)
                text = ""
                for page in reader.pages:
                    extracted = page.extract_text()
                    if extracted:
                        text += extracted + "\n"
                
                # Analitzar amb el motor de Gemini passant el model triat
                analysis = analyze_cv_with_gemini(text, job_description, model_name=selected_model)
                
                # Afegir metadades addicionals
                analysis["Arxiu"] = file.name
                results.append(analysis)
                
            except Exception as e:
                results.append({
                    "nom": "Error de lectura",
                    "puntuacio": 0,
                    "punts_forts": "N/A",
                    "alertes": f"No s'ha pogut llegir el PDF: {str(e)}",
                    "resum_fitxa": "Error en l'extracció del document.",
                    "Arxiu": file.name
                })
            
            progress_bar.progress((i + 1) / total_files)
            
        status_text.text("✅ Anàlisi completada amb èxit!")
        st.success(f"S'han analitzat {total_files} candidats correctament.")
        
        # Convertir a DataFrame i ordenar per puntuació descendent
        df = pd.DataFrame(results)
        
        # Assegurar ordre de columnes
        cols = ["nom", "puntuacio", "punts_forts", "alertes", "resum_fitxa", "Arxiu"]
        existing_cols = [c for c in cols if c in df.columns]
        df = df[existing_cols].sort_values(by="puntuacio", ascending=False).reset_index(drop=True)
        
        st.subheader("📊 Rànquing i Avaluació de Candidats")
        
        # Mostrar taula interactiva
        st.dataframe(
            df,
            use_container_width=True,
            column_config={
                "nom": "Candidat/a",
                "puntuacio": st.column_config.NumberColumn("Puntuació (0-10)", format="%d 🏆"),
                "punts_forts": "Punts Forts",
                "alertes": "Bretxes / Alertes",
                "resum_fitxa": "Veredicte RRHH",
                "Arxiu": "Fitxer CV"
            }
        )
        
        # Detall expandible per candidat
        st.markdown("---")
        st.subheader("🔍 Detall Individual per Candidat")
        for idx, row in df.iterrows():
            with st.expander(f"#{idx+1} - {row['nom']} (Puntuació: {row['puntuacio']}/10) - {row['Arxiu']}"):
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f"**💪 Punts Forts:**\n{row['punts_forts']}")
                    st.markdown(f"**⚠️ Alertes / Bretxes:**\n{row['alertes']}")
                with col2:
                    st.markdown(f"**📝 Veredicte per a l'Entrevistador:**\n{row['resum_fitxa']}")
else:
    st.info("💡 **Instruccions:** Revisa l'oferta de feina a la barra lateral i puja un o diversos CVs en PDF per començar l'anàlisi.")