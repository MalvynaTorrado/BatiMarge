import streamlit as st
import pandas as pd
import os

# --- 1. CONFIGURATION ET RÉPARATION DES FICHIERS ---
st.set_page_config(page_title="BatiMarge Pro", layout="centered")

CLIENTS_FILE = "clients.csv"
DEVIS_FILE = "devis_archives.csv"
CATALOGUE_FILE = "catalogue.csv"

def verifier_et_reparer_fichiers():
    # Cette fonction s'assure que les fichiers ont toujours les bons titres de colonnes
    fichiers = {
        CLIENTS_FILE: ["Nom", "Contact"],
        DEVIS_FILE: ["Client", "Article", "Vente HT", "Marge", "Nom Devis"],
        CATALOGUE_FILE: ["Article", "Prix Achat HT"]
    }
    for fichier, colonnes in fichiers.items():
        # Si le fichier n'existe pas ou est vide, on le crée proprement avec ses titres
        if not os.path.exists(fichier) or os.stat(fichier).st_size == 0:
            pd.DataFrame(columns=colonnes).to_csv(fichier, index=False)
        else:
            # Sécurité supplémentaire : on vérifie si les colonnes sont les bonnes
            try:
                df_test = pd.read_csv(fichier)
                for col in colonnes:
                    if col not in df_test.columns:
                        pd.DataFrame(columns=colonnes).to_csv(fichier, index=False)
                        break
            except:
                pd.DataFrame(columns=colonnes).to_csv(fichier, index=False)

# On répare tout avant d'afficher l'interface
verifier_et_reparer_fichiers()

if 'panier' not in st.session_state:
    st.session_state['panier'] = []

# --- 2. STYLE DESIGN ---
st.markdown("""
    <style>
    .stApp { background-color: #F8F9FA; }
    .stButton>button {
        width: 100%; background: linear-gradient(135deg, #FF8C00 0%, #FF4500 100%);
        color: white; border-radius: 12px; border: none; font-weight: bold; padding: 12px;
    }
    div[data-testid="metric-container"] {
        background-color: white; padding: 20px; border-radius: 15px; box-shadow: 0 4px 10px rgba(0,0,0,0.05);
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. MENU LATÉRAL ---
with st.sidebar:
    if os.path.exists("logo.png"):
        st.image("logo.png", width=200)
    st.title("🏗️ BatiMarge Pro")
    st.divider()
    menu = st.radio("NAVIGATION", ["Tableau de bord", "Fiches Clients", "Catalogue", "Nouveau Devis", "Archives", "Scan-Marge"])

# --- 4. LOGIQUE DES PAGES ---

if menu == "Tableau de bord":
    st.title("Bonjour 👋")
    df_c = pd.read_csv(CLIENTS_FILE)
    st.metric("Total Clients", len(df_c))
    st.info("Utilisez le menu à gauche pour commencer vos chiffrages.")

elif menu == "Fiches Clients":
    st.title("👥 Gestion des Clients")
    with st.expander("➕ Ajouter un client"):
        nom = st.text_input("Nom / Entreprise")
        tel = st.text_input("Téléphone")
        if st.button("Enregistrer"):
            if nom:
                pd.DataFrame([{"Nom": nom, "Contact": tel}]).to_csv(CLIENTS_FILE, mode='a', header=False, index=False)
                st.success(f"Client {nom} ajouté !")
                st.rerun()

    df_c = pd.read_csv(CLIENTS_FILE)
    st.table(df_c)

elif menu == "Catalogue":
    st.title("📚 Catalogue Matériaux")
    with st.expander("➕ Ajouter au catalogue"):
        art_cat = st.text_input("Désignation")
        prix_cat = st.number_input("Prix Achat HT", min_value=0.0)
        if st.button("Valider"):
            pd.DataFrame([{"Article": art_cat, "Prix Achat HT": prix_cat}]).to_csv(CATALOGUE_FILE, mode='a', header=False, index=False)
            st.success("Article enregistré !")
            st.rerun()
    st.dataframe(pd.read_csv(CATALOGUE_FILE), use_container_width=True)

elif menu == "Nouveau Devis":
    st.title("📝 Nouveau Devis")
    df_c = pd.read_csv(CLIENTS_FILE)
    
    if df_c.empty:
        st.warning("⚠️ Créez d'abord un client dans 'Fiches Clients'.")
    else:
        client_choisi = st.selectbox("Client :", df_c["Nom"].unique())
        art = st.text_input("Article")
        p_achat = st.number_input("Prix Achat HT (€)", min_value=0.0)
        coeff = st.number_input("Coeff. Marge", min_value=1.0, value=1.5)
        
        p_vente = p_achat * coeff
        st.subheader(f"Vente suggérée : {p_vente:.2f} € HT")
        
        if st.button("🛒 Ajouter au panier"):
            st.session_state['panier'].append({"Client": client_choisi, "Article": art, "Vente HT": p_vente, "Marge": p_vente - p_achat})
            st.success("Ajouté !")

elif menu == "Archives":
    st.title("🗄️ Archives")
    df_a = pd.read_csv(DEVIS_FILE)
    if not df_a.empty:
        st.write(df_a)
    else:
        st.info("Aucune archive pour le moment.")

elif menu == "Scan-Marge":
    st.title("📸 Scan")
    st.camera_input("Scanner un document")













