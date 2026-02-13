import streamlit as st
import pandas as pd
import os

# --- 1. CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="BatiMarge Pro", layout="centered")

# --- 2. INITIALISATION DES FICHIERS DE DONNÉES ---
CLIENTS_FILE = "clients.csv"
DEVIS_FILE = "devis_archives.csv"
CATALOGUE_FILE = "catalogue.csv"

def initialiser_fichiers():
    if not os.path.exists(CLIENTS_FILE) or os.stat(CLIENTS_FILE).st_size == 0:
        pd.DataFrame(columns=["Nom", "Contact"]).to_csv(CLIENTS_FILE, index=False)
    if not os.path.exists(DEVIS_FILE) or os.stat(DEVIS_FILE).st_size == 0:
        pd.DataFrame(columns=["Client", "Article", "Vente HT", "Marge", "Nom Devis"]).to_csv(DEVIS_FILE, index=False)
    if not os.path.exists(CATALOGUE_FILE) or os.stat(CATALOGUE_FILE).st_size == 0:
        pd.DataFrame(columns=["Article", "Prix Achat HT"]).to_csv(CATALOGUE_FILE, index=False)

initialiser_fichiers()

if 'panier' not in st.session_state:
    st.session_state['panier'] = []

# --- 3. STYLE PERSONNALISÉ (DESIGN) ---
st.markdown("""
    <style>
    .stApp { background-color: #F8F9FA; }
    [data-testid="stMetricValue"] { color: #FF8C00 !important; font-weight: bold; }
    div[data-testid="metric-container"] {
        background-color: white; padding: 20px; border-radius: 15px; 
        box-shadow: 0 4px 6px rgba(0,0,0,0.05); border: 1px solid #EEE;
    }
    .stButton>button {
        width: 100%; background: linear-gradient(135deg, #FF8C00 0%, #FF4500 100%);
        color: white; border-radius: 12px; height: 3em; font-weight: bold; border: none;
    }
    .result-box {
        background-color:#FFF3E0; padding:20px; border-radius:15px; 
        border-left: 5px solid #FF8C00; margin-bottom:20px; text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 4. NAVIGATION & CHARGEMENT DU LOGO ---
with st.sidebar:
    # --- BLOC CHARGEMENT DU LOGO ---
    try:
        if os.path.exists("logo.png"):
            st.image("logo.png", width=200)
        else:
            st.warning("Fichier 'logo.png' non trouvé sur GitHub")
    except Exception as e:
        st.error(f"Erreur logo : {e}")
    
    st.title("🏗️ BatiMarge")
    st.subheader("Expert Rentabilité")
    st.divider()
    
    menu = st.radio("Aller vers :", [
        "Tableau de bord", 
        "Fiches Clients",
        "Catalogue Matériaux",
        "Nouveau Devis", 
        "Archives Devis",
        "Scan-Marge"
    ])
    st.divider()
    st.caption("Version Pro 3.5")

# --- 5. LOGIQUE DES PAGES ---

# --- PAGE : TABLEAU DE BORD ---
if menu == "Tableau de bord":
    st.title("Bonjour, Constructeur 👋")
    col1, col2, col3 = st.columns(3)
    df_c = pd.read_csv(CLIENTS_FILE)
    df_cat = pd.read_csv(CATALOGUE_FILE)
    
    with col1:
        st.metric("Clients", len(df_c))
    with col2:
        st.metric("Catalogue", len(df_cat))
    with col3:
        st.metric("Articles Panier", len(st.session_state['panier']))

# --- PAGE : FICHES CLIENTS ---
elif menu == "Fiches Clients":
    st.title("👥 Gestion des Clients")
    with st.expander("➕ Créer un nouveau client"):
        n_nom = st.text_input("Nom / Entreprise")
        n_tel = st.text_input("Téléphone")
        if st.button("Enregistrer le client"):
            if n_nom:
                pd.DataFrame([{"Nom": n_nom, "Contact": n_tel}]).to_csv(CLIENTS_FILE, mode='a', header=False, index=False)
                st.success("Client ajouté !")
                st.rerun()

    df_c = pd.read_csv(CLIENTS_FILE)
    st.table(df_c)

# --- PAGE : CATALOGUE ---
elif menu == "Catalogue Matériaux":
    st.title("📚 Catalogue Matériaux")
    with st.expander("➕ Ajouter un article au catalogue"):
        c_art = st.text_input("Nom du matériau")
        c_prix = st.number_input("Prix Achat HT habituel (€)", min_value=0.0)
        if st.button("Ajouter au catalogue"):
            if c_art:
                pd.DataFrame([{"Article": c_art, "Prix Achat HT": c_prix}]).to_csv(CATALOGUE_FILE, mode='a', header=False, index=False)
                st.success("Article enregistré !")
                st.rerun()
    
    df_cat = pd.read_csv(CATALOGUE_FILE)
    st.dataframe(df_cat, use_container_width=True)

# --- PAGE : NOUVEAU DEVIS ---
elif menu == "Nouveau Devis":
    st.title("📝 Nouveau Devis")
    df_c = pd.read_csv(CLIENTS_FILE)
    df_cat = pd.read_csv(CATALOGUE_FILE)
    
    if df_c.empty:
        st.warning("⚠️ Créez un client d'abord dans 'Fiches Clients'.")
    else:
        client_choisi = st.selectbox("Client :", df_c["Nom"].unique())
        
        st.subheader("Choix de l'article")
        source = st.radio("Source :", ["Depuis le catalogue", "Saisie manuelle"])
        
        if source == "Depuis le catalogue" and not df_cat.empty:
            art_obj = st.selectbox("Sélectionner l'article :", df_cat["Article"].unique())
            prix_base = df_cat[df_cat["Article"] == art_obj]["Prix Achat HT"].values[0]
            art_nom = art_obj
        else:
            art_nom = st.text_input("Nom de l'article")
            prix_base = st.number_input("Prix Achat HT (€)", min_value=0.0)

        coeff = st.number_input("Coeff. Marge", min_value=1.0, value=1.5, step=0.1)
        p_vente = prix_base * coeff
        
        st.markdown(f"""<div class="result-box"><p>PRIX DE VENTE CONSEILLÉ</p><h2>{p_vente:.2f} € HT</h2></div>""", unsafe_allow_html=True)
        
        if st.button("🛒 AJOUTER AU DEVIS"):
            if art_nom:
                st.session_state['panier'].append({"Client": client_choisi, "Article": art_nom, "Vente HT": p_vente, "Marge": p_vente - prix_base})
                st.success("Ajouté au panier !")
            else:
                st.error("Précisez le nom de l'article.")

        if st.session_state['panier']:
            st.divider()
            st.write("### Récapitulatif du panier")
            st.table(pd.DataFrame(st.session_state['panier']))
            nom_devis_final = st.text_input("Nom du devis (ex: Toiture Dupont) :")
            if st.button("💾 ARCHIVER LE DEVIS"):
                if nom_devis_final:
                    df_save = pd.DataFrame(st.session_state['panier'])
                    df_save["Nom Devis"] = nom_devis_final
                    df_save.to_csv(DEVIS_FILE, mode='a', header=False, index=False)
                    st.session_state['panier'] = []
                    st.success("Devis sauvegardé !")
                    st.rerun()
                else:
                    st.error("Donnez un nom au devis.")

# --- PAGE : ARCHIVES ---
elif menu == "Archives Devis":
    st.title("🗄️ Archives")
    if os.path.exists(DEVIS_FILE) and os.stat(DEVIS_FILE).st_size > 50:
        df_a = pd.read_csv(DEVIS_FILE)
        choix = st.selectbox("Sélectionner un devis :", df_a["Nom Devis"].unique())
        st.table(df_a[df_a["Nom Devis"] == choix])
    else:
        st.info("Aucune archive disponible.")

# --- PAGE : SCAN-MARGE ---
elif menu == "Scan-Marge":
    st.title("📸 Scan-Marge")
    st.camera_input("Prendre une photo du document")












