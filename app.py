import streamlit as st
import pandas as pd
import os

# --- 1. CONFIGURATION ET INITIALISATION ---
st.set_page_config(page_title="BatiMarge Expert", layout="centered")

CLIENTS_FILE = "clients.csv"
DEVIS_FILE = "devis_archives.csv"

# Fonction magique pour créer les fichiers avec leurs colonnes si besoin
def initialiser_fichiers():
    if not os.path.exists(CLIENTS_FILE) or os.stat(CLIENTS_FILE).st_size == 0:
        pd.DataFrame(columns=["Nom", "Contact"]).to_csv(CLIENTS_FILE, index=False)
    if not os.path.exists(DEVIS_FILE) or os.stat(DEVIS_FILE).st_size == 0:
        pd.DataFrame(columns=["Client", "Article", "Vente HT", "Marge", "Nom Devis"]).to_csv(DEVIS_FILE, index=False)

initialiser_fichiers()

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
    try:
        st.image("logo.png", width=180)
    except:
        st.title("🏗️ BatiMarge")
    st.divider()
    menu = st.radio("MENU", ["Tableau de bord", "Clients", "Calculateur", "Mon Devis", "Archives"])

# --- 4. LOGIQUE DES PAGES ---

if menu == "Tableau de bord":
    st.title("Bonjour 👋")
    st.write("Bienvenue dans votre gestionnaire de marge.")
    st.metric("Articles en attente", len(st.session_state['panier']))

elif menu == "Clients":
    st.title("👥 Clients")
    with st.expander("➕ Ajouter un client"):
        nom = st.text_input("Nom de l'entreprise / Client")
        tel = st.text_input("Téléphone")
        if st.button("Enregistrer"):
            if nom:
                nouveau = pd.DataFrame([{"Nom": nom, "Contact": tel}])
                nouveau.to_csv(CLIENTS_FILE, mode='a', header=False, index=False)
                st.success("Client enregistré !")
                st.rerun()

    df_c = pd.read_csv(CLIENTS_FILE)
    if not df_c.empty:
        st.table(df_c)
    else:
        st.info("Aucun client enregistré.")

elif menu == "Calculateur":
    st.title("📝 Calcul")
    df_c = pd.read_csv(CLIENTS_FILE)
    
    if df_c.empty:
        st.warning("Ajoutez d'abord un client dans l'onglet 'Clients'.")
    else:
        client_sel = st.selectbox("Client", df_c["Nom"].unique())
        art = st.text_input("Désignation")
        p_achat = st.number_input("Achat HT", min_value=0.0)
        coeff = st.number_input("Coeff", min_value=1.0, value=1.5)
        p_vente = p_achat * coeff
        
        st.subheader(f"Prix de vente : {p_vente:.2f} € HT")
        
        if st.button("🛒 AJOUTER AU PANIER"):
            st.session_state['panier'].append({
                "Client": client_sel, "Article": art, "Vente HT": p_vente, "Marge": p_vente - p_achat
            })
            st.success("Ajouté !")

elif menu == "Mon Devis":
    st.title("📂 Panier en cours")
    if st.session_state['panier']:
        df_p = pd.DataFrame(st.session_state['panier'])
        st.table(df_p)
        nom_d = st.text_input("Nom du devis (ex: Chantier Durand)")
        if st.button("💾 ARCHIVER LE DEVIS"):
            df_p["Nom Devis"] = nom_d
            df_p.to_csv(DEVIS_FILE, mode='a', header=False, index=False)
            st.session_state['panier'] = []
            st.success("Archivé !")
            st.rerun()
    else:
        st.info("Panier vide.")

elif menu == "Archives":
    st.title("🗄️ Archives")
    if os.path.exists(DEVIS_FILE):
        try:
            df_a = pd.read_csv(DEVIS_FILE)
            if not df_a.empty:
                st.write(df_a)
            else:
                st.info("Aucune archive.")
        except:
            st.info("Fichier archive vide.")






