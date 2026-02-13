import streamlit as st
import pandas as pd
import os

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="BatiMarge Pro", layout="centered")

CLIENTS_FILE = "clients.csv"
DEVIS_FILE = "devis_archives.csv"
CATALOGUE_FILE = "catalogue.csv"
PANIER_TEMP_FILE = "panier_temp.csv"

def verifier_fichiers():
    fichiers = {
        CLIENTS_FILE: ["Nom", "Contact"],
        DEVIS_FILE: ["Client", "Article", "Vente HT", "Marge", "Nom Devis"],
        CATALOGUE_FILE: ["Article", "Prix Achat HT"],
        PANIER_TEMP_FILE: ["Client", "Article", "Vente HT", "Marge"]
    }
    for f, cols in fichiers.items():
        if not os.path.exists(f) or os.stat(f).st_size == 0:
            pd.DataFrame(columns=cols).to_csv(f, index=False)

verifier_fichiers()

# Initialisation de la navigation interne pour les archives
if 'devis_selectionne' not in st.session_state:
    st.session_state['devis_selectionne'] = None

# --- 2. STYLE ---
st.markdown("""
    <style>
    .stApp { background-color: #F8F9FA; }
    .stButton>button { border-radius: 12px; font-weight: bold; }
    .btn-retour { background-color: #6c757d !important; color: white !important; }
    .panier-header { background-color: #333; color: white; padding: 10px; border-radius: 10px; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. MENU ---
with st.sidebar:
    if os.path.exists("logo.png"): st.image("logo.png", width=200)
    st.title("🏗️ BatiMarge Pro")
    menu = st.radio("NAVIGATION", ["Tableau de bord", "Fiches Clients", "Catalogue", "Nouveau Devis", "Archives", "Scan-Marge"])

# --- 4. LOGIQUE DES PAGES ---

# --- PAGE ARCHIVES (Avec Vue Détail) ---
if menu == "Archives":
    df_archives = pd.read_csv(DEVIS_FILE)
    
    # SI UN DEVIS EST SÉLECTIONNÉ : ON AFFICHE LA PAGE DÉTAIL
    if st.session_state['devis_selectionne'] is not None:
        nom_d = st.session_state['devis_selectionne']
        st.button("⬅️ Retour à la liste", on_click=lambda: st.session_state.update({"devis_selectionne": None}))
        
        st.title(f"📄 Devis : {nom_d}")
        donnees_devis = df_archives[df_archives["Nom Devis"] == nom_d]
        
        st.table(donnees_devis[["Client", "Article", "Vente HT", "Marge"]])
        
        total = donnees_devis["Vente HT"].sum()
        marge_totale = donnees_devis["Marge"].sum()
        
        c1, c2 = st.columns(2)
        c1.metric("Total Devis HT", f"{total:.2f} €")
        c2.metric("Marge Totale", f"{marge_totale:.2f} €")
        
        st.download_button("📥 Télécharger (CSV)", donnees_devis.to_csv(index=False), f"{nom_d}.csv", "text/csv")

    # SINON : ON AFFICHE LA LISTE DES DEVIS
    else:
        st.title("🗄️ Archives des Devis")
        if not df_archives.empty:
            noms_uniques = df_archives["Nom Devis"].unique()
            
            for nom in noms_uniques:
                col_nom, col_btn = st.columns([3, 1])
                col_nom.write(f"📁 **{nom}**")
                if col_btn.button("👁️ Ouvrir", key=nom):
                    st.session_state['devis_selectionne'] = nom
                    st.rerun()
        else:
            st.info("Aucun devis archivé.")

# --- PAGE NOUVEAU DEVIS ---
elif menu == "Nouveau Devis":
    st.title("📝 Nouveau Devis")
    df_c = pd.read_csv(CLIENTS_FILE)
    if df_c.empty:
        st.warning("⚠️ Créez un client d'abord.")
    else:
        client = st.selectbox("Client :", df_c["Nom"].unique())
        art = st.text_input("Article")
        pa = st.number_input("Achat HT", min_value=0.0)
        co = st.number_input("Coeff", min_value=1.0, value=1.5)
        pv = pa * co
        
        if st.button("🛒 AJOUTER"):
            pd.DataFrame([{"Client": client, "Article": art, "Vente HT": pv, "Marge": pv-pa}]).to_csv(PANIER_TEMP_FILE, mode='a', header=False, index=False)
            st.rerun()
        
        st.write("---")
        df_p = pd.read_csv(PANIER_TEMP_FILE)
        if not df_p.empty:
            st.table(df_p)
            n_d = st.text_input("Nom du chantier :")
            if st.button("💾 ARCHIVER LE DEVIS"):
                df_p["Nom Devis"] = n_d
                df_p.to_csv(DEVIS_FILE, mode='a', header=False, index=False)
                pd.DataFrame(columns=["Client", "Article", "Vente HT", "Marge"]).to_csv(PANIER_TEMP_FILE, index=False)
                st.success("Archivé !")
                st.rerun()

# (Les autres pages restent identiques au code précédent...)
elif menu == "Fiches Clients":
    st.title("👥 Clients")
    n = st.text_input("Nom")
    if st.button("Ajouter"):
        pd.DataFrame([{"Nom": n, "Contact": ""}]).to_csv(CLIENTS_FILE, mode='a', header=False, index=False)
        st.rerun()
    st.table(pd.read_csv(CLIENTS_FILE))

elif menu == "Tableau de bord":
    st.title("🏠 Accueil")
    st.write("Bienvenue.")

elif menu == "Scan-Marge":
    st.title("📸 Scan")
    st.camera_input("Scanner")

elif menu == "Catalogue":
    st.title("📚 Catalogue")
    st.table(pd.read_csv(CATALOGUE_FILE))











