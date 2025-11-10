# 1) Image Python légère
FROM python:3.11-slim

# 2) Éviter les questions interactives
ENV DEBIAN_FRONTEND=noninteractive

# 3) Installer quelques dépendances système utiles
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 4) Créer un dossier de travail
WORKDIR /app

# 5) Copier le fichier des dépendances d’abord
COPY requirements.txt .

# 6) Installer les dépendances Python
RUN pip install --no-cache-dir -r requirements.txt

# 7) Copier le reste du projet (code, CSV, etc.)
COPY . .

# 8) Exposer le port Streamlit (dans le container)
EXPOSE 8501

# 9) Commande de lancement
CMD ["streamlit", "run", "mon_projet_saas.py", "--server.port=8501", "--server.address=0.0.0.0"]
