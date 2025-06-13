import streamlit as st
import pandas as pd
import os
import time
from dotenv import load_dotenv
import openai
from pathlib import Path
import tempfile
import json

# Charger les variables d'environnement
load_dotenv()

# Configuration de la page Streamlit
st.set_page_config(
    page_title="Traducteur CSV en Masse",
    page_icon="🌐",
    layout="wide"
)

# Styles CSS
st.markdown("""
<style>
    .main {
        padding: 2rem;
    }
    .title {
        font-size: 2.5rem;
        font-weight: bold;
        margin-bottom: 1rem;
        color: #1E88E5;
    }
    .subtitle {
        font-size: 1.5rem;
        margin-bottom: 2rem;
        color: #424242;
    }
    .info-box {
        background-color: #E3F2FD;
        padding: 1rem;
        border-radius: 5px;
        margin-bottom: 1rem;
    }
    .success-box {
        background-color: #E8F5E9;
        padding: 1rem;
        border-radius: 5px;
        margin-bottom: 1rem;
    }
    .warning-box {
        background-color: #FFF8E1;
        padding: 1rem;
        border-radius: 5px;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# Titre de l'application
st.markdown('<div class="title">Traducteur CSV en Masse</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Traduisez facilement vos fichiers CSV avec GPT ou LLAMA</div>', unsafe_allow_html=True)

# Fonction pour initialiser les variables de session
def init_session_state():
    if 'api_key' not in st.session_state:
        st.session_state.api_key = os.getenv("OPENAI_API_KEY", "")
    if 'model_choice' not in st.session_state:
        st.session_state.model_choice = "gpt-3.5-turbo"
    if 'llama_model_path' not in st.session_state:
        st.session_state.llama_model_path = ""
    if 'df' not in st.session_state:
        st.session_state.df = None
    if 'columns_to_translate' not in st.session_state:
        st.session_state.columns_to_translate = []
    if 'source_lang' not in st.session_state:
        st.session_state.source_lang = "Français"
    if 'target_lang' not in st.session_state:
        st.session_state.target_lang = "Anglais"
    if 'progress' not in st.session_state:
        st.session_state.progress = 0
    if 'translated_df' not in st.session_state:
        st.session_state.translated_df = None
    if 'translation_complete' not in st.session_state:
        st.session_state.translation_complete = False

# Initialiser les variables de session
init_session_state()

# Fonction pour traduire le texte avec GPT-3.5
def translate_with_gpt(text, source_lang, target_lang, api_key):
    if not text or pd.isna(text) or text.strip() == "":
        return text
    
    # Utiliser l'API OpenAI avec la clé fournie
    client = openai.OpenAI(api_key=api_key)
    
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": f"Tu es un traducteur professionnel du {source_lang} vers le {target_lang}. Traduis uniquement le texte fourni sans ajouter d'explications."},
                {"role": "user", "content": text}
            ],
            temperature=0.3,
            max_tokens=500
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        st.error(f"Erreur lors de la traduction avec GPT: {str(e)}")
        return text

# Fonction pour traduire le texte avec LLAMA
def translate_with_llama(text, source_lang, target_lang, model_path):
    if not text or pd.isna(text) or text.strip() == "":
        return text
    
    try:
        from llama_cpp import Llama
        
        llm = Llama(model_path=model_path, n_ctx=2048)
        
        prompt = f"""
        Traduis le texte suivant du {source_lang} vers le {target_lang}. 
        Ne donne que la traduction, sans explications.
        
        Texte: {text}
        
        Traduction:
        """
        
        output = llm(prompt, max_tokens=500, temperature=0.3, stop=["Texte:", "\n\n"])
        return output["choices"][0]["text"].strip()
    except Exception as e:
        st.error(f"Erreur lors de la traduction avec LLAMA: {str(e)}")
        return text

# Sidebar pour les paramètres
with st.sidebar:
    st.header("Paramètres")
    
    # Choix du modèle
    model_choice = st.radio(
        "Choisissez le modèle de traduction:",
        ["GPT-3.5", "LLAMA (Local)"],
        index=0 if st.session_state.model_choice == "gpt-3.5-turbo" else 1
    )
    
    st.session_state.model_choice = "gpt-3.5-turbo" if model_choice == "GPT-3.5" else "llama"
    
    # Configuration selon le modèle choisi
    if st.session_state.model_choice == "gpt-3.5-turbo":
        api_key = st.text_input(
            "Clé API OpenAI:",
            value=st.session_state.api_key,
            type="password",
            help="Entrez votre clé API OpenAI pour utiliser GPT-3.5"
        )
        st.session_state.api_key = api_key
        
        # Avertissement pour Streamlit Cloud
        if not api_key:
            st.warning("⚠️ Dans Streamlit Cloud, vous devez ajouter votre clé API dans les secrets de l'application.")
            st.info("Pour les tests locaux, vous pouvez l'entrer ici.")
    else:
        # Avertissement pour LLAMA sur Streamlit Cloud
        st.warning("⚠️ LLAMA n'est pas disponible sur Streamlit Cloud. Cette option ne fonctionne qu'en local.")
        
        llama_model_path = st.text_input(
            "Chemin vers le modèle LLAMA:",
            value=st.session_state.llama_model_path,
            help="Entrez le chemin complet vers votre fichier modèle LLAMA (.gguf)"
        )
        st.session_state.llama_model_path = llama_model_path
        
        if not os.path.exists(llama_model_path) and llama_model_path:
            st.warning("Le chemin du modèle LLAMA spécifié n'existe pas.")
    
    # Langues
    st.subheader("Langues")
    languages = ["Français", "Anglais", "Espagnol", "Allemand", "Italien", "Portugais", "Néerlandais", "Russe", "Chinois", "Japonais", "Arabe"]
    
    source_lang = st.selectbox(
        "Langue source:",
        languages,
        index=languages.index(st.session_state.source_lang) if st.session_state.source_lang in languages else 0
    )
    st.session_state.source_lang = source_lang
    
    target_lang = st.selectbox(
        "Langue cible:",
        languages,
        index=languages.index(st.session_state.target_lang) if st.session_state.target_lang in languages else 1
    )
    st.session_state.target_lang = target_lang

# Onglets principaux
tab1, tab2, tab3 = st.tabs(["Importer CSV", "Traduire", "Exporter"])

# Onglet 1: Importer CSV
with tab1:
    st.header("Étape 1: Importer votre fichier CSV")
    
    uploaded_file = st.file_uploader("Choisissez un fichier CSV", type="csv")
    
    if uploaded_file is not None:
        try:
            # Créer un fichier temporaire pour stocker le contenu
            with tempfile.NamedTemporaryFile(delete=False, suffix='.csv') as tmp_file:
                tmp_file.write(uploaded_file.getvalue())
                tmp_filepath = tmp_file.name
            
            # Options d'encodage et de séparateur
            encoding_options = ["utf-8", "latin1", "iso-8859-1", "cp1252"]
            separator_options = [",", ";", "\t", "|"]
            
            col1, col2 = st.columns(2)
            with col1:
                encoding = st.selectbox("Encodage du fichier:", encoding_options)
            with col2:
                separator = st.selectbox("Séparateur:", separator_options)
            
            # Charger le DataFrame
            if st.button("Charger le fichier"):
                try:
                    df = pd.read_csv(tmp_filepath, encoding=encoding, sep=separator)
                    st.session_state.df = df
                    
                    # Afficher un aperçu
                    st.success(f"Fichier chargé avec succès! {len(df)} lignes et {len(df.columns)} colonnes.")
                    st.subheader("Aperçu des données:")
                    st.dataframe(df.head(5))
                    
                    # Nettoyer le fichier temporaire
                    os.unlink(tmp_filepath)
                except Exception as e:
                    st.error(f"Erreur lors du chargement du fichier: {str(e)}")
                    st.info("Essayez de modifier l'encodage ou le séparateur.")
        except Exception as e:
            st.error(f"Erreur lors du traitement du fichier: {str(e)}")

# Onglet 2: Traduire
with tab2:
    st.header("Étape 2: Configurer et lancer la traduction")
    
    if st.session_state.df is not None:
        # Sélection des colonnes à traduire
        st.subheader("Sélectionnez les colonnes à traduire:")
        
        all_columns = st.session_state.df.columns.tolist()
        
        # Remplacer le multiselect par des cases à cocher pour chaque colonne
        columns_to_translate = []
        st.write("Cochez les colonnes que vous souhaitez traduire:")
        
        # Organiser les cases à cocher en grille (3 colonnes)
        col_containers = st.columns(3)
        
        for i, col_name in enumerate(all_columns):
            # Déterminer dans quelle colonne de la grille placer cette case à cocher
            container_idx = i % 3
            
            # Vérifier si cette colonne était précédemment sélectionnée
            default_value = col_name in st.session_state.columns_to_translate
            
            # Créer la case à cocher dans la colonne appropriée
            with col_containers[container_idx]:
                if st.checkbox(col_name, value=default_value, key=f"col_{col_name}"):
                    columns_to_translate.append(col_name)
        
        # Mettre à jour la session state avec les colonnes sélectionnées
        st.session_state.columns_to_translate = columns_to_translate
        
        # Afficher un résumé des colonnes sélectionnées
        if columns_to_translate:
            st.success(f"Colonnes sélectionnées pour traduction: {', '.join(columns_to_translate)}")
        else:
            st.warning("Aucune colonne sélectionnée pour traduction.")
        
        # Vérification des paramètres avant traduction
        can_translate = True
        error_message = ""
        
        if not columns_to_translate:
            can_translate = False
            error_message = "Veuillez sélectionner au moins une colonne à traduire."
        
        if st.session_state.model_choice == "gpt-3.5-turbo" and not st.session_state.api_key:
            can_translate = False
            error_message = "Veuillez entrer votre clé API OpenAI pour utiliser GPT-3.5."
        
        if st.session_state.model_choice == "llama" and not os.path.exists(st.session_state.llama_model_path):
            can_translate = False
            error_message = "Veuillez spécifier un chemin valide vers un modèle LLAMA."
        
        if st.session_state.source_lang == st.session_state.target_lang:
            can_translate = False
            error_message = "Les langues source et cible doivent être différentes."
        
        # Afficher un message d'erreur si nécessaire
        if not can_translate and error_message:
            st.warning(error_message)
        
        # Bouton pour lancer la traduction
        if can_translate and st.button("Lancer la traduction"):
            # Créer une copie du DataFrame original
            translated_df = st.session_state.df.copy()
            
            # Barre de progression
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Nombre total d'éléments à traduire
            total_items = len(st.session_state.df) * len(columns_to_translate)
            processed_items = 0
            
            # Traduire chaque colonne sélectionnée
            for col in columns_to_translate:
                status_text.text(f"Traduction de la colonne: {col}")
                
                for idx, value in enumerate(st.session_state.df[col]):
                    # Mettre à jour le statut
                    row_num = idx + 1
                    status_text.text(f"Traduction de la colonne '{col}', ligne {row_num}/{len(st.session_state.df)}")
                    
                    # Traduire le texte selon le modèle choisi
                    if st.session_state.model_choice == "gpt-3.5-turbo":
                        translated_text = translate_with_gpt(
                            str(value),
                            st.session_state.source_lang,
                            st.session_state.target_lang,
                            st.session_state.api_key
                        )
                    else:
                        translated_text = translate_with_llama(
                            str(value),
                            st.session_state.source_lang,
                            st.session_state.target_lang,
                            st.session_state.llama_model_path
                        )
                    
                    # Mettre à jour le DataFrame traduit
                    translated_df.at[idx, col] = translated_text
                    
                    # Mettre à jour la progression
                    processed_items += 1
                    progress = processed_items / total_items
                    progress_bar.progress(progress)
                    st.session_state.progress = progress
                    
                    # Petite pause pour éviter de surcharger l'API
                    if st.session_state.model_choice == "gpt-3.5-turbo":
                        time.sleep(0.5)
            
            # Enregistrer le DataFrame traduit dans la session
            st.session_state.translated_df = translated_df
            st.session_state.translation_complete = True
            
            # Afficher un message de succès
            status_text.text("Traduction terminée!")
            st.success("Toutes les colonnes ont été traduites avec succès!")
            
            # Afficher un aperçu des résultats
            st.subheader("Aperçu des données traduites:")
            st.dataframe(translated_df.head(5))
        
        # Afficher les résultats si la traduction est déjà terminée
        elif st.session_state.translation_complete and st.session_state.translated_df is not None:
            st.success("Traduction déjà effectuée. Vous pouvez exporter les résultats dans l'onglet 'Exporter'.")
            st.subheader("Aperçu des données traduites:")
            st.dataframe(st.session_state.translated_df.head(5))
    else:
        st.info("Veuillez d'abord importer un fichier CSV dans l'onglet 'Importer CSV'.")

# Onglet 3: Exporter
with tab3:
    st.header("Étape 3: Exporter les résultats")
    
    if st.session_state.translation_complete and st.session_state.translated_df is not None:
        # Options d'exportation
        st.subheader("Options d'exportation:")
        
        col1, col2 = st.columns(2)
        with col1:
            export_encoding = st.selectbox("Encodage pour l'export:", ["utf-8", "latin1", "iso-8859-1", "cp1252"])
        with col2:
            export_separator = st.selectbox("Séparateur pour l'export:", [",", ";", "\t", "|"])
        
        # Nom du fichier
        export_filename = st.text_input("Nom du fichier d'export:", "translated_data.csv")
        
        # Bouton pour exporter
        if st.button("Exporter le fichier CSV"):
            try:
                # Créer un fichier CSV temporaire
                csv_data = st.session_state.translated_df.to_csv(index=False, sep=export_separator, encoding=export_encoding)
                
                # Offrir le téléchargement
                st.download_button(
                    label="Télécharger le fichier CSV",
                    data=csv_data,
                    file_name=export_filename,
                    mime="text/csv"
                )
                
                st.success(f"Fichier '{export_filename}' prêt à être téléchargé!")
            except Exception as e:
                st.error(f"Erreur lors de l'exportation: {str(e)}")
    else:
        st.info("Aucune donnée traduite disponible. Veuillez d'abord effectuer une traduction dans l'onglet 'Traduire'.")

# Pied de page
st.markdown("---")
st.markdown("Développé avec ❤️ | Ecom Translator GPT")
