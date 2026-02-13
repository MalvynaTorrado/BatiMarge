import streamlit as st
import pandas as pd
import os

# --- 1. CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="BatiMarge Pro", layout="centered")

# --- 2. INITIALISATION AUTOMATIQUE DES FICHIERS (Anti-Erreur) ---
CLIENTS_FILE = "clients.csv"
DEVIS_FILE = "devis_archives.csv"
CATALOGUE_FILE = "catalogue.csv"

def initialiser_systeme():
    # Crée les fichiers avec les colonnes nécessaires s'ils n'existent pas ou sont vides
    if not os.path.exists(CLIENTS_FILE) or os.stat(CLIENTS_FILE).st_size == 0:
        pd.DataFrame(columns=["Nom", "Contact"]).to_csv(CLIENTS_FILE, index=False)
    
    if not os.path.exists(DEVIS_FILE) or os.stat(DEVIS_FILE).st_size == 0:
        pd.DataFrame(columns=["Client", "Article", "Vente HT", "Marge", "Nom Devis"]).to_csv(DEVIS_FILE, index=False)
    
    if not os.path.exists(CATALOGUE_FILE) or os.stat(CATALOGUE_FILE).st_size == 0:
        pd.DataFrame(columns=["Article", "Prix Achat HT"]).to_csv(CATALOGUE_FILE, index=False)

# On lance l'initialisation dès le départ
initialiser_systeme()

# Mémoire vive pour le panier en cours
if 'panier' not in st.session_state:
    st.session_state['panier'] = []

# --- 3. STYLE PERSONNALISÉ (DESIGN ARTISAN) ---
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

# --- 4. BARRE LATÉRALE : LOGO ET NAVIGATION ---
with st.sidebar:
    # Chargement du Logo
    if os.path.exists("logo.png"):
        st.image("logo.png", width=200)
    else:
        st.info("Logo : Ajoutez 'logo.png' sur GitHub")
    
    st.title("🏗️ BatiMarge Pro")
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
    st.caption("Version 4.0 - Stable")

# --- 5. LOGIQUE DES PAGES ---

# --- PAGE : TABLEAU DE BORD ---
if menu == "Tableau de bord":
    st.title("Bonjour, Constructeur 👋")
    col1, col2, col3 = st.columns(3)
    
    df_c = pd.read_csv(CLIENTS_FILE)
    df_cat = pd.read_csv(CATALOGUE_FILE)
    total_panier = sum(item['Vente HT'] for item in st.session_state['panier'])
    
    col1.metric("Clients", len(df_c))
    col2.metric("Catalogue", len(df_cat))
    col3.metric("Panier HT", f"{total_panier:.0f} €")
    
    st.write("---")
    st.write("Bienvenue dans votre outil de gestion. Utilisez le menu à gauche pour naviguer.")

# --- PAGE : FICHES CLIENTS ---
elif menu == "Fiches Clients":
    st.title("👥 Gestion des Clients")
    with st.expander("➕ Enregistrer un nouveau client", expanded=True):
        n_nom = st.text_input("Nom de l'entreprise ou du particulier")
        n_tel = st.text_input("Téléphone / Contact")
        if st.button("Valider la création"):
            if n_nom:
                nouveau = pd.DataFrame([{"Nom": n_nom, "Contact": n_tel}])
                nouveau.to_csv(CLIENTS_FILE, mode='a', header=False, index=False)
                st.success(f"Client '{n_nom}' enregistré !")
                st.rerun()
            else:
                st.error("Le nom est obligatoire.")

    st.subheader("Vos contacts")
    df_c = pd.read_csv(CLIENTS_FILE)
    if not df_c.empty:
        st.table(df_c)
    else:
        st.info("Aucun client pour le moment.")

# --- PAGE : CATALOGUE ---
elif menu == "Catalogue Matériaux":
    st.title("📚 Catalogue Matériaux")
    with st.expander("➕ Ajouter au catalogue"):
        c_art = st.text_input("Nom du matériau")
        c_prix = st.number_input("Prix Achat HT habituel (€)", min_value=0.0, step=0.1)
        if st.button("Enregistrer au catalogue"):
            if c_art:
                pd.DataFrame([{"Article": c_art, "Prix Achat HT": c_prix}]).to_csv(CATALOGUE_FILE, mode='a', header=False, index=False)
                st.success("Matériau ajouté !")
                st.rerun()

    df_cat = pd.read_csv(CATALOGUE_FILE)
    if not df_cat.empty:
        st.dataframe(df_cat, use_container_width=True)
    else:
        st.info("Le catalogue est vide.")

# --- PAGE : NOUVEAU DEVIS ---
elif menu == "Nouveau Devis":
    st.title("📝 Nouveau Devis")
    df_c = pd.read_csv(CLIENTS_FILE)
    df_cat = pd.read_csv(CATALOGUE_FILE)
    
    if df_c.empty:
        st.warning("⚠️ Veuillez d'abord créer un client dans l'onglet 'Fiches Clients'.")
    else:
        client_choisi = st.selectbox("Sélectionner le client :", df_c["Nom"].unique())
        
        st.divider()
        source = st.radio("Choix de l'article :", ["Saisie manuelle", "Depuis le catalogue"])
        
        if source == "Depuis le catalogue" and not df_cat.empty:
            art_sel = st.selectbox("Article du catalogue :", df_cat["Article"].unique())
            prix_base = df_cat[df_cat["Article"] == art_sel]["Prix Achat HT"].values[0]
            art_final = art_sel
        else:
            art_final = st.text_input("Désignation de l'article")
            prix_base = st.number_input("Prix Achat HT (€)", min_value=0.0)

        coeff = st.number_input("Coefficient de marge", min_value=1.0, value=1.5, step=0.1)
        p_vente = prix_base * coeff
        
        st.markdown(f"""
        <div class="result-box">
            <p style="margin:0; font-size:14px;">PRIX DE VENTE CONSEILLÉ</p>
            <h2 style="margin:0; color:#E65100;">{p_vente:.2f} € HT</h2>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🛒 AJOUTER AU PANIER"):
            if art_final:
                st.session_state['panier'].append({
                    "Client": client_choisi, "Article": art_final, "Vente HT": p_vente, "Marge": p_vente - prix_base
                })
                st.success("Ajouté !")
            else:
                st.error("Veuillez nommer l'article.")

        if st.session_state['panier']:
            st.write("---")
            st.subheader("Articles du devis en cours")
            df_panier = pd.DataFrame(st.session_state['panier'])
            st.table(df_panier)
            
            nom_devis = st.text_input("Nom du devis (ex: Chantier Durand) :")
            if st.button("💾 ARCHIVER LE DEVIS"):
                if nom_devis:
                    df_panier["Nom Devis"] = nom_devis
                    df_panier.to_csv(DEVIS_FILE, mode='a', header=False, index=False)
                    st.session_state['panier'] = []
                    st.success("Devis sauvegardé dans les archives !")
                    st.rerun()
                else:
                    st.error("Donnez un nom au devis.")

# --- PAGE : ARCHIVES ---
elif menu == "Archives Devis":
    st.title("🗄️ Archives")
    if os.path.exists(DEVIS_FILE):
        df_a = pd.read_csv(DEVIS_FILE)
        if not df_a.empty:
            liste_devis = df_a["Nom Devis"].unique()
            choix = st.selectbox("Ouvrir un devis :", liste_devis)
            recap = df_a[df_a["Nom Devis"] == choix]
            st.table(recap)
            st.metric("Total Devis HT", f"{recap['Vente HT'].sum():.2f} €")
        else:
            st.info("Aucun devis archivé.")

# --- PAGE : SCAN-MARGE ---
elif menu == "Scan-Marge":
    st.title("📸 Scan-Marge")
    st.camera_input("Scanner un document ou une étiquette")












