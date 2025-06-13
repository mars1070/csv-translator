# Guide de déploiement sur Streamlit Cloud

Ce guide explique comment déployer l'application "Ecom Translator GPT" sur Streamlit Cloud.

## Prérequis

1. Un compte GitHub
2. Un compte Streamlit Cloud (gratuit)
3. Une clé API OpenAI

## Étapes de déploiement

### 1. Créer un dépôt GitHub

1. Créez un nouveau dépôt sur GitHub
2. Poussez le code de l'application vers ce dépôt
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin https://github.com/VOTRE-USERNAME/ecom-translator-gpt.git
   git push -u origin main
   ```

### 2. Déployer sur Streamlit Cloud

1. Connectez-vous à [Streamlit Cloud](https://streamlit.io/cloud)
2. Cliquez sur "New app"
3. Sélectionnez votre dépôt GitHub
4. Dans le champ "Main file path", entrez `app.py`
5. Cliquez sur "Advanced settings" et configurez les secrets:
   ```toml
   [openai]
   api_key = "votre-clé-api-openai"
   ```
6. Cliquez sur "Deploy"

### 3. Configuration des secrets

Pour que l'application fonctionne correctement, vous devez configurer votre clé API OpenAI dans les secrets de Streamlit Cloud :

1. Dans le dashboard de Streamlit Cloud, sélectionnez votre application
2. Cliquez sur les trois points (...) puis sur "Settings"
3. Allez dans l'onglet "Secrets"
4. Ajoutez votre clé API OpenAI dans le format suivant :
   ```toml
   [openai]
   api_key = "votre-clé-api-openai"
   ```
5. Cliquez sur "Save"

### 4. Limitations

- L'option LLAMA n'est pas disponible sur Streamlit Cloud car elle nécessite un accès au système de fichiers local
- Les fichiers CSV très volumineux peuvent être limités par les ressources de Streamlit Cloud

### 5. Mise à jour de l'application

Pour mettre à jour l'application déployée, il suffit de pousser les modifications vers votre dépôt GitHub. Streamlit Cloud détectera automatiquement les changements et redéploiera l'application.
