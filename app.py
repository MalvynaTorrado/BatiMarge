import streamlit as st
import pandas as pd
import os
from datetime import datetime

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="BatiMarge Pro", layout="centered")

CLIENTS_FILE = "clients.csv"
DEVIS_FILE = "devis_archives.csv"
PANIER_TEMP_FILE = "panier_temp.csv"

# --- 2. RÉPARATION ET INITIALISATION DES FICHIERS ---
def initialiser_fichiers():
    fichiers = {
        CLIENTS_FILE: ["Nom", "Contact"],
        DEVIS_FILE: ["Client", "Article", "Vente HT", "Marge", "Nom Devis"],
        PANIER_TEMP_FILE: ["Client", "Article", "Vente HT", "Marge"]
    }
    for f, cols in fichiers.items():
        if not os.path.exists(f) or os.stat(f).st_size < 2:
            pd.DataFrame(columns=cols).to_csv(f, index=False)

initialiser_fichiers()

if 'devis_selectionne' not in st.session_state:
    st.session_state['devis_selectionne'] = None

# --- 3. MENU LATÉRAL ---
with st.sidebar:
    st.title("🏗️ BatiMarge Pro")
    menu = st.radio("MENU", ["Clients", "Nouveau Devis", "Archives"])
    st.divider()
    if st.button("🔄 Actualiser l'app"):
        st.rerun()

# --- 4. PAGE CLIENTS ---
if menu == "Clients":
    st.title("👥 Gestion Clients")
    with st.form("nouveau_client"):
        nom = st.text_input("Nom du client")
        contact = st.text_input("Contact")
        if st.form_submit_button("Enregistrer"):
            if nom:
                pd.DataFrame([{"Nom": nom, "Contact": contact}]).to_csv(CLIENTS_FILE, mode='a', header=False, index=False)
                st.success("Client ajouté !")
                st.rerun()

    st.subheader("Liste")
    st.table(pd.read_csv(CLIENTS_FILE))

# --- 5. PAGE NOUVEAU DEVIS ---
elif menu == "Nouveau Devis":
    st.title("📝 Nouveau Devis")
    df_c = pd.read_csv(CLIENTS_FILE)
    
    if df_c.empty:
        st.warning("Ajoutez d'abord un client dans l'onglet 'Clients'.")
    else:
        client = st.selectbox("Choisir le client :", df_c["Nom"].unique())
        art = st.text_input("Désignation")
        pa = st.number_input("Prix Achat HT", min_value=0.0)
        co = st.number_input("Coefficient", min_value=1.0, value=1.5)
        pv = pa * co
        
        st.info(f"Prix de vente suggéré : {pv:.2f} € HT")
        
        if st.button("🛒 AJOUTER AU PANIER"):
            if art:
                pd.DataFrame([{"Client": client, "Article": art, "Vente HT": pv, "Marge": pv-pa}]).to_csv(PANIER_TEMP_FILE, mode='a', header=False, index=False)
                st.rerun()

        st.divider()
        df_p = pd.read_csv(PANIER_TEMP_FILE)
        if not df_p.empty:
            st.write("### Panier actuel")
            st.table(df_p)
            nom_d = st.text_input("Nom du chantier (ex: Toiture Dupont)")
            if st.button("💾 SAUVEGARDER LE DEVIS"):
                if nom_d:
                    df_p["Nom Devis"] = nom_d
                    df_p.to_csv(DEVIS_FILE, mode='a', header=False, index=False)
                    pd.DataFrame(columns=["Client", "Article", "Vente HT", "Marge"]).to_csv(PANIER_TEMP_FILE, index=False)
                    st.success("Devis archivé !")
                    st.rerun()

# --- 6. PAGE ARCHIVES ---
elif menu == "Archives":
    df_a = pd.read_csv(DEVIS_FILE)
    
    if st.session_state['devis_selectionne']:
        nom_sel = st.session_state['devis_selectionne']
        if st.button("⬅️ Retour"):
            st.session_state['devis_selectionne'] = None
            st.rerun()
            
        data = df_a[df_a["Nom Devis"] == nom_sel]
        st.header(f"Devis : {nom_sel}")
        st.table(data[["Article", "Vente HT"]])
        st.metric("TOTAL HT", f"{data['Vente HT'].sum():.2f} €")
        
    else:
        st.title("🗄️ Archives")
        if not df_a.empty:
            for n in df_a["Nom Devis"].unique():
                col1, col2 = st.columns([3, 1])
                col1.write(f"📁 {n}")
                if col2.button("Ouvrir", key=n):
                    st.session_state['devis_selectionne'] = n
                    st.rerun()
        else:
            st.info("Aucun devis.")



