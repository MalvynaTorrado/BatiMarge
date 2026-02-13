import streamlit as st
import pandas as pd
import os

# --- 1. CONFIGURATION DE L'APPLI ---
st.set_page_config(page_title="BatiMarge Expert", layout="centered")

# Noms des fichiers de stockage
CLIENTS_FILE = "clients.csv"
DEVIS_FILE = "devis_archives.csv"

# Initialisation de la mémoire vive pour la session
if 'panier' not in st.session_state:
    st.session_state['panier'] = []

# --- 2. STYLE VISUEL (Finitions) ---
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
    .result-box {
        background-color:#FFF3E0; padding:20px; border-radius:15px; border-left: 5px solid #FF8C00; margin-bottom:20px;
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
    menu = st.radio("MENU PRINCIPAL", ["Tableau de bord", "Clients", "Calculateur", "Mon Devis en cours", "Archives"])
    st.divider()
    st.caption("Propulsé par Gemini - Version Expert")

# --- 4. LOGIQUE DES PAGES ---

# --- PAGE : TABLEAU DE BORD ---
if menu == "Tableau de bord":
    st.title("Bonjour 👋")
    col1, col2 = st.columns(2)
    total_art = len(st.session_state['panier'])
    
    # Calcul rapide du total panier
    total_encours = sum(item['Vente HT'] for item in st.session_state['panier']) if st.session_state['panier'] else 0
    
    col1.metric("Articles au panier", total_art)
    col2.metric("Total Devis en cours", f"{total_encours:.2f} €")
    st.info("Utilisez le menu à gauche pour naviguer.")

# --- PAGE : CLIENTS ---
elif menu == "Clients":
    st.title("👥 Gestion des Clients")
    
    with st.expander("➕ Ajouter un nouveau client"):
        nom = st.text_input("Nom / Entreprise")
        tel = st.text_input("Téléphone / Contact")
        if st.button("Enregistrer le client"):
            if nom:
                nouveau = pd.DataFrame([{"Nom": nom, "Contact": tel}])
                header = not os.path.exists(CLIENTS_FILE) or os.stat(CLIENTS_FILE).st_size == 0
                nouveau.to_csv(CLIENTS_FILE, mode='a', header=header, index=False)
                st.success(f"Client {nom} ajouté !")
                st.rerun()
            else:
                st.error("Le nom est obligatoire.")

    st.subheader("Vos clients enregistrés")
    if os.path.exists(CLIENTS_FILE) and os.stat(CLIENTS_FILE).st_size > 0:
        df_c = pd.read_csv(CLIENTS_FILE)
        st.table(df_c)
    else:
        st.info("Aucun client pour le moment.")

# --- PAGE : CALCULATEUR ---
elif menu == "Calculateur":
    st.title("📝 Chiffrage Article")
    
    # On récupère les clients pour la liste déroulante
    if os.path.exists(CLIENTS_FILE) and os.stat(CLIENTS_FILE).st_size > 0:
        liste_clients = pd.read_csv(CLIENTS_FILE)["Nom"].tolist()
        client_sel = st.selectbox("Sélectionner le client", liste_clients)
        
        art = st.text_input("Désignation de l'article")
        c1, c2 = st.columns(2)
        p_achat = c1.number_input("Prix Achat HT (€)", min_value=0.0)
        coeff = c2.number_input("Coeff. Marge", min_value=1.0, value=1.5, step=0.1)
        
        p_vente = p_achat * coeff
        marge = p_vente - p_achat
        
        st.markdown(f"""
        <div class="result-box">
            <p style="margin:0; color:#E65100; font-size:14px;">PRIX DE VENTE CONSEILLÉ</p>
            <h2 style="margin:0; color:#E65100;">{p_vente:.2f} € HT</h2>
            <p style="margin:0; color:#555;">Marge : {marge:.2f} €</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🛒 AJOUTER AU DEVIS"):
            st.session_state['panier'].append({
                "Client": client_sel, "Article": art, "Achat HT": p_achat, "Vente HT": p_vente, "Marge": marge
            })
            st.success("Article ajouté au devis en cours !")
    else:
        st.warning("⚠️ Allez dans 'Clients' pour créer votre premier client avant de calculer.")

# --- PAGE : MON DEVIS EN COURS ---
elif menu == "Mon Devis en cours":
    st.title("📂 Devis en préparation")
    if st.session_state['panier']:
        df_p = pd.DataFrame(st.session_state['panier'])
        st.table(df_p)
        
        total_p = df_p["Vente HT"].sum()
        st.subheader(f"Total HT : {total_p:.2f} €")
        
        nom_devis = st.text_input("Nom du devis pour l'archive (ex: Rénovation Salon)")
        if st.button("💾 SAUVEGARDER DANS LES ARCHIVES"):
            if nom_devis:
                df_p["Nom Devis"] = nom_devis
                header = not os.path.exists(DEVIS_FILE) or os.stat(DEVIS_FILE).st_size == 0
                df_p.to_csv(DEVIS_FILE, mode='a', header=header, index=False)
                st.session_state['panier'] = []
                st.success("Devis archivé ! Vous le retrouverez dans 'Archives'.")
                st.rerun()
            else:
                st.error("Donnez un nom au devis pour l'enregistrer.")
    else:
        st.info("Le devis actuel est vide.")

# --- PAGE : ARCHIVES ---
elif menu == "Archives":
    st.title("🗄️ Archives des Devis")
    if os.path.exists(DEVIS_FILE) and os.stat(DEVIS_FILE).st_size > 0:
        df_a = pd.read_csv(DEVIS_FILE)
        noms_devis = df_a["Nom Devis"].unique()
        choix = st.selectbox("Ouvrir un ancien devis", noms_devis)
        
        recap = df_a[df_a["Nom Devis"] == choix]
        st.table(recap)
        st.write(f"**Total HT de ce devis : {recap['Vente HT'].sum():.2f} €**")
        
        if st.button("🗑️ Supprimer TOUTES les archives"):
            os.remove(DEVIS_FILE)
            st.rerun()
    else:
        st.info("Aucun devis archivé pour le moment.")




