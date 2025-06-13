# Ecom Translator GPT

Une application pour traduire en masse des fichiers CSV en utilisant GPT-3.5 ou un modèle LLAMA local.

## Fonctionnalités

- Importation de fichiers CSV avec différentes options d'encodage et de séparateurs
- Sélection des colonnes spécifiques à traduire
- Choix entre GPT-3.5 (nécessite une clé API OpenAI) et LLAMA (modèle local gratuit)
- Prise en charge de multiples langues
- Exportation des résultats dans un nouveau fichier CSV

## Installation

1. Installez les dépendances :

```bash
pip install -r requirements.txt
```

2. Pour utiliser LLAMA, vous devez télécharger un modèle au format GGUF. Vous pouvez en trouver sur [HuggingFace](https://huggingface.co/models?sort=downloads&search=gguf).

## Utilisation

1. Lancez l'application :

```bash
streamlit run app.py
```

2. Suivez les étapes dans l'interface :
   - Importez votre fichier CSV
   - Sélectionnez les colonnes à traduire
   - Choisissez les langues source et cible
   - Lancez la traduction
   - Exportez le résultat

## Configuration

### Utilisation de GPT-3.5
- Nécessite une clé API OpenAI
- Plus précis pour les traductions complexes
- Limité par les quotas de l'API OpenAI

### Utilisation de LLAMA (gratuit)
- Nécessite un modèle LLAMA au format GGUF
- Fonctionne entièrement en local sans coût
- Performances variables selon le modèle utilisé

## Remarques

- Pour les gros fichiers CSV, la traduction peut prendre du temps
- Avec GPT-3.5, une pause de 0.5 seconde est ajoutée entre chaque traduction pour éviter de dépasser les limites de l'API
- Les modèles LLAMA nécessitent une quantité significative de RAM selon leur taille
