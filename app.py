
import streamlit as st
import pandas as pd
from datetime import datetime

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="BatiMarge - Expert Rentabilité", page_icon="🏗️")

# --- STYLE PERSONNALISÉ (Couleurs BatiMarge) ---
st.markdown("""
    <style>
    .main { background-color: #f5f5f5; }
    .stButton>button { background-color: #FF8C00; color: white; border-radius: 5px; }
    .stMetric { background-color: white; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
    </style>
    """, unsafe_allow_html=True)

# --- TITRE ET LOGO ---
st.title("🏗️ BatiMarge")
st.caption("L'assistant qui sécurise vos chantiers et vos bénéfices.")

# --- NAVIGATION ---
menu = ["Tableau de bord", "Nouveau Devis", "Scan-Marge", "Mon Catalogue"]
choice = st.sidebar.selectbox("Menu", menu)

# --- INITIALISATION DES DONNÉES (Session State) ---
if 'devis_items' not in st.session_state:
    st.session_state.devis_items = []

# --- 1. TABLEAU DE BORD ---
if choice == "Tableau de bord":
    st.header("Statistiques du mois")
    col1, col2, col3 = st.columns(3)
    col1.metric("Devis envoyés", "12")
    col2.metric("Chiffre d'Affaires", "14 500 €")
    col3.metric("Marge moyenne", "32%", "+2%")
    
    st.info("💡 Conseil BatiMarge : Le prix du cuivre a augmenté de 5%. Pensez à ajuster vos devis d'électricité.")

# --- 2. NOUVEAU DEVIS ---
elif choice == "Nouveau Devis":
    st.header("Créer un devis")
    
    with st.expander("👤 Informations Client", expanded=True):
        nom_client = st.text_input("Nom du client")
        adresse = st.text_area("Adresse du chantier")

    with st.container():
        st.subheader("📦 Articles")
        nom_art = st.text_input("Désignation de l'article")
        col_p1, col_p2, col_p3 = st.columns(3)
        
        prix_achat = col_p1.number_input("Prix Achat HT (€)", min_value=0.0, step=0.1)
        coeff = col_p2.number_input("Coeff. Marge", min_value=1.0, value=1.5, step=0.1)
        quantite = col_p3.number_input("Quantité", min_value=1, value=1)
        
        prix_vente_unit = prix_achat * coeff
        
        if st.button("➕ Ajouter l'article"):
            item = {
                "Désignation": nom_art,
                "Quantité": quantite,
                "Prix Achat HT": prix_achat,
                "Prix Vente HT": prix_vente_unit,
                "Total HT": prix_vente_unit * quantite
            }
            st.session_state.devis_items.append(item)
            st.success("Article ajouté !")

    # Affichage du tableau du devis
    if st.session_state.devis_items:
        df = pd.DataFrame(st.session_state.devis_items)
        st.table(df[["Désignation", "Quantité", "Prix Vente HT", "Total HT"]])
        
        total_devis = df["Total HT"].sum()
        st.subheader(f"Total Devis : {total_devis:,.2f} € HT")
        
        if st.button("💾 Générer le PDF (Simulé)"):
            st.balloons()
            st.success(f"Devis pour {nom_client} prêt à être envoyé !")

# --- 3. SCAN-MARGE (Killer Feature) ---
elif choice == "Scan-Marge":
    st.header("📸 Scan-Marge")
    st.write("Scannez le code-barres d'un produit pour l'ajouter avec votre marge.")
    
    img_file = st.camera_input("Prise de vue du code-barres")
    
    if img_file:
        st.warning("Recherche du produit dans la base de données...")
        # Simulation de détection
        st.success("Produit détecté : Sac de Ciment 35kg")
        p_achat_simule = 8.50
        st.write(f"Prix d'achat constaté : **{p_achat_simule} € HT**")
        
        marge_pref = st.slider("Ajuster la marge pour ce produit", 1.0, 3.0, 1.8)
        st.info(f"Prix de vente suggéré : **{(p_achat_simule * marge_pref):.2f} € HT**")
        
        if st.button("Ajouter ce prix au devis"):
             st.success("Ciment ajouté au devis en cours.")

# --- 4. CATALOGUE ---
elif choice == "Mon Catalogue":
    st.header("🗂️ Mes Tarifs Matériaux")
    st.write("Importez ou modifiez votre liste de prix fournisseurs.")
    uploaded_file = st.file_view = st.file_uploader("Importer un fichier Excel/CSV", type=["csv", "xlsx"])
# --- 1. CONFIGURATION ET STOCKAGE ---
st.set_page_config(page_title="BatiMarge Expert", layout="centered")

# Fichiers de sauvegarde (pour ne rien perdre)
CLIENTS_FILE = "clients.csv"
DEVIS_FILE = "devis_enregistres.csv"

# Initialisation des fichiers s'ils n'existent pas
for file in [CLIENTS_FILE, DEVIS_FILE]:
    if not os.path.exists(file):
        pd.DataFrame().to_csv(file, index=False)

# Mémoire vive pour la session en cours
if 'panier' not in st.session_state:
    st.session_state['panier'] = []

# --- 2. STYLE DESIGN ---
st.markdown("""
    <style>
    .stApp { background-color: #F8F9FA; }
    .stButton>button {
        width: 100%; background: linear-gradient(135deg, #007bff 0%, #0056b3 100%);
        color: white; border-radius: 10px; border: none; font-weight: bold;
    }
    .main-title { color: #007bff; font-weight: bold; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. MENU LATÉRAL ---
with st.sidebar:
    try:
        st.image("logo.png", width=150)
    except:
        st.title("🏗️ BatiMarge")
    st.divider()
    menu = st.radio("MENU", ["Clients", "Calculateur", "Mon Devis en cours", "Archives Devis"])

# --- 4. LOGIQUE DES PAGES ---

# --- PAGE : CLIENTS ---
if menu == "Clients":
    st.title("👥 Gestion des Clients")
    
    with st.expander("➕ Ajouter un nouveau client"):
        nom = st.text_input("Nom / Entreprise")
        tel = st.text_input("Téléphone")
        if st.button("Enregistrer le client"):
            if nom:
                nouveau_client = pd.DataFrame([{"Nom": nom, "Contact": tel}])
                # On ajoute le client et on crée les titres de colonnes s'ils n'existent pas
                nouveau_client.to_csv(CLIENTS_FILE, mode='a', header=not os.path.exists(CLIENTS_FILE) or os.stat(CLIENTS_FILE).st_size == 0, index=False)
                st.success("Client enregistré ! Rafraîchissez la page.")
            else:
                st.error("Le nom est obligatoire.")

    st.subheader("Liste de vos clients")
    
    # --- LA SÉCURITÉ ANTI-ERREUR ICI ---
    try:
        if os.path.exists(CLIENTS_FILE) and os.stat(CLIENTS_FILE).st_size > 0:
            df_c = pd.read_csv(CLIENTS_FILE)
            st.table(df_c)
        else:
            st.info("Votre liste de clients est vide pour le moment.")
    except Exception:
        st.info("Commencez par ajouter votre premier client ci-dessus.")
    st.subheader("Liste de vos clients")
    df_c = pd.read_csv(CLIENTS_FILE)
    if not df_c.empty:
        st.table(df_c)
    else:
        st.info("Aucun client enregistré.")

# --- PAGE : CALCULATEUR ---
elif menu == "Calculateur":
    st.title("📝 Chiffrage Article")
    df_c = pd.read_csv(CLIENTS_FILE)
    
    if df_c.empty:
        st.warning("⚠️ Créez d'abord un client dans l'onglet 'Clients'.")
    else:
        client_choisi = st.selectbox("Pour quel client ?", df_c["Nom"])
        art = st.text_input("Désignation")
        c1, c2 = st.columns(2)
        p_achat = c1.number_input("Achat HT (€)", min_value=0.0)
        coeff = c2.number_input("Coeff.", min_value=1.0, value=1.5)
        
        p_vente = p_achat * coeff
        st.metric("Prix de Vente conseillé", f"{p_vente:.2f} €")
        
        if st.button("Ajouter au devis"):
            st.session_state['panier'].append({
                "Client": client_choisi, "Article": art, "Vente HT": p_vente
            })
            st.success("Ajouté au panier !")

# --- PAGE : MON DEVIS EN COURS ---
elif menu == "Mon Devis en cours":
    st.title("📂 Devis Actuel")
    if st.session_state['panier']:
        df_p = pd.DataFrame(st.session_state['panier'])
        st.table(df_p)
        
        nom_devis = st.text_input("Nommer ce devis (ex: Toiture Dumont)")
        if st.button("💾 SAUVEGARDER ET FERMER LE DEVIS"):
            df_p["Nom Devis"] = nom_devis
            df_p.to_csv(DEVIS_FILE, mode='a', header=False, index=False)
            st.session_state['panier'] = []
            st.success("Devis archivé avec succès !")
            st.rerun()
    else:
        st.info("Le devis est vide.")

# --- PAGE : ARCHIVES ---
elif menu == "Archives Devis":
    st.title("🗄️ Archives des Devis")
    if os.path.exists(DEVIS_FILE):
        df_a = pd.read_csv(DEVIS_FILE, names=["Client", "Article", "Vente HT", "Nom Devis"])
        if not df_a.empty:
            selection = st.selectbox("Choisir un devis à ouvrir", df_a["Nom Devis"].unique())
            st.write(f"Détails pour : **{selection}**")
            st.table(df_a[df_a["Nom Devis"] == selection])
        else:
            st.info("Aucune archive trouvée.")





