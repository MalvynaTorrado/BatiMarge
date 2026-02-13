import streamlit as st
import pandas as pd
import os

# --- 1. CONFIGURATION ET RÉPARATION ---
st.set_page_config(page_title="BatiMarge Pro", layout="centered")

CLIENTS_FILE = "clients.csv"
DEVIS_FILE = "devis_archives.csv"
CATALOGUE_FILE = "catalogue.csv"

def verifier_et_reparer_fichiers():
    fichiers = {
        CLIENTS_FILE: ["Nom", "Contact"],
        DEVIS_FILE: ["Client", "Article", "Vente HT", "Marge", "Nom Devis"],
        CATALOGUE_FILE: ["Article", "Prix Achat HT"]
    }
    for fichier, colonnes in fichiers.items():
        if not os.path.exists(fichier) or os.stat(fichier).st_size == 0:
            pd.DataFrame(columns=colonnes).to_csv(fichier, index=False)

verifier_et_reparer_fichiers()

# --- MÉMOIRE VIVE DU PANIER ---
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
    .panier-header {
        background-color: #333; color: white; padding: 10px; border-radius: 10px 10px 0 0;
        text-align: center; margin-top: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. MENU LATÉRAL ---
with st.sidebar:
    if os.path.exists("logo.png"):
        st.image("logo.png", width=200)
    st.title("🏗️ BatiMarge Pro")
    menu = st.radio("NAVIGATION", ["Tableau de bord", "Fiches Clients", "Catalogue", "Nouveau Devis", "Archives", "Scan-Marge"])

# --- 4. LOGIQUE DES PAGES ---

if menu == "Nouveau Devis":
    st.title("📝 Nouveau Devis")
    df_c = pd.read_csv(CLIENTS_FILE)
    
    if df_c.empty:
        st.warning("⚠️ Créez d'abord un client dans 'Fiches Clients'.")
    else:
        # --- PARTIE CALCUL ---
        client_choisi = st.selectbox("Client :", df_c["Nom"].unique())
        art = st.text_input("Désignation de l'article")
        col1, col2 = st.columns(2)
        p_achat = col1.number_input("Prix Achat HT (€)", min_value=0.0)
        coeff = col2.number_input("Coeff. Marge", min_value=1.0, value=1.5)
        
        p_vente = p_achat * coeff
        st.subheader(f"Vente suggérée : {p_vente:.2f} € HT")
        
        if st.button("🛒 AJOUTER AU PANIER"):
            if art:
                # On ajoute à la liste en mémoire
                st.session_state['panier'].append({
                    "Client": client_choisi, 
                    "Article": art, 
                    "Vente HT": p_vente, 
                    "Marge": p_vente - p_achat
                })
                st.success(f"'{art}' ajouté !")
                st.rerun() # On force le rafraîchissement pour voir le panier
            else:
                st.error("Donnez un nom à l'article.")

        # --- PARTIE VISUELLE DU PANIER (Juste en dessous) ---
        st.write("---")
        st.markdown('<div class="panier-header">🛒 VOTRE PANIER EN COURS</div>', unsafe_allow_html=True)
        
        if st.session_state['panier']:
            df_visu = pd.DataFrame(st.session_state['panier'])
            st.table(df_visu) # On utilise st.table pour que ce soit bien lisible
            
            total_ht = df_visu["Vente HT"].sum()
            st.subheader(f"Total Panier : {total_ht:.2f} € HT")
            
            nom_devis = st.text_input("Nommer ce devis pour l'enregistrer :")
            col_a, col_b = st.columns(2)
            
            if col_a.button("💾 ENREGISTRER DANS LES ARCHIVES"):
                if nom_devis:
                    df_visu["Nom Devis"] = nom_devis
                    df_visu.to_csv(DEVIS_FILE, mode='a', header=False, index=False)
                    st.session_state['panier'] = [] # On vide après sauvegarde
                    st.success("Devis archivé !")
                    st.rerun()
                else:
                    st.error("Nommez le devis.")
            
            if col_b.button("🗑️ VIDER LE PANIER"):
                st.session_state['panier'] = []
                st.rerun()
        else:
            st.info("Le panier est vide. Ajoutez un article ci-dessus.")

# (Garder les autres pages comme avant...)
elif menu == "Tableau de bord":
    st.title("Tableau de bord")
    st.write("Bienvenue.")
elif menu == "Fiches Clients":
    st.title("Clients")
    # ... (code client identique au précédent)
    nom = st.text_input("Nom")
    if st.button("OK"):
        pd.DataFrame([{"Nom": nom, "Contact": ""}]).to_csv(CLIENTS_FILE, mode='a', header=False, index=False)
        st.rerun()
    st.table(pd.read_csv(CLIENTS_FILE))
elif menu == "Archives":
    st.title("Archives")
    st.table(pd.read_csv(DEVIS_FILE))











