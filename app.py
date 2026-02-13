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