# Utilitzem una imatge oficial i lleugera de Python
FROM python:3.11-slim

# Directori de treball dins del contenidor
WORKDIR /app

# Instal·lar dependències del sistema necessàries
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copiar el fitxer de dependències i instal·lar-les
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar la resta del codi font a l'interior del contenidor
COPY . .

# Exposar el port predeterminat de Streamlit
EXPOSE 8501

# Comanda per engegar l'aplicació Streamlit
CMD ["streamlit", "run", "app.py", "--server.address=0.0.0.0", "--server.port=8501"]