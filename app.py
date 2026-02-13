import streamlit as st
import pandas as pd
import os
from datetime import datetime

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

if 'devis_selectionne' not in st.session_state:
    st.session_state['devis_selectionne'] = None

# --- 2. STYLE CSS ---
st.markdown("""
    <style>
    .stApp { background-color: #F8F9FA; }
    .stButton>button { border-radius: 12px; font-weight: bold; }
    @media print {
        .no-print { display: none !important; }
        .print-only { display: block !important; }
    }
    .devis-box {
        background-color: white; padding: 40px; border: 1px solid #EEE;
        border-radius: 10px; color: black; font-family: sans-serif;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. MENU LATÉRAL ---
with st.sidebar:
    if os.path.exists("logo.png"): st.image("logo.png", width=200)
    st.title("🏗️ BatiMarge Pro")
    menu = st.radio("NAVIGATION", ["Tableau de bord", "Fiches Clients", "Catalogue", "Nouveau Devis", "Archives", "Scan-Marge"])

# --- 4. LOGIQUE DES PAGES ---

if menu == "Archives":
    df_archives = pd.read_csv(DEVIS_FILE)
    
    if st.session_state['devis_selectionne'] is not None:
        nom_d = st.session_state['devis_selectionne']
        
        # BOUTONS DE NAVIGATION
        col_nav1, col_nav2 = st.columns([1,1])
        with col_nav1:
            if st.button("⬅️ Retour à la liste"):
                st.session_state['devis_selectionne'] = None
                st.rerun()
        with col_nav2:
            st.info("💡 Pour le PDF : Faites 'Clic droit' -> 'Imprimer' -> 'Enregistrer en PDF'")

        # --- PRÉPARATION DES DONNÉES DU DEVIS ---
        donnees = df_archives[df_archives["Nom Devis"] == nom_d]
        client_nom = donnees["Client"].iloc[0]
        date_jour = datetime.now().strftime("%d/%m/%Y")
        total_ht = donnees["Vente HT"].sum()
        
        # --- DESIGN DU DEVIS HTML (FORMAT PDF) ---
        lignes_html = ""
        for _, row in donnees.iterrows():
            lignes_html += f"""
            <tr>
                <td style="padding:10px; border-bottom:1px solid #EEE;">{row['Article']}</td>
                <td style="padding:10px; border-bottom:1px solid #EEE; text-align:right;">{row['Vente HT']:.2f} €</td>
            </tr>
            """

        devis_template = f"""
        <div class="devis-box">
            <table style="width:100%;">
                <tr>
                    <td style="width:50%;">
                        <h2 style="color:#FF4500; margin:0;">DEVIS PRO</h2>
                        <p style="font-size:12px; color:#555;">Document généré par BatiMarge</p>
                    </td>
                    <td style="width:50%; text-align:right;">
                        <p><b>Date :</b> {date_jour}</p>
                        <p><b>Devis n° :</b> {nom_d.upper()}</p>
                    </td>
                </tr>
            </table>
            <br><br>
            <div style="background:#F9F9F9; padding:15px; border-radius:5px;">
                <p style="margin:0; color:#777; font-size:12px;">DESTINATAIRE</p>
                <h3 style="margin:0;">{client_nom}</h3>
            </div>
            <br>
            <table style="width:100%; border-collapse: collapse;">
                <tr style="background:#333; color:white;">
<th style="padding:10px; text-align:left;">Désignation</th>
                    <th style="padding:10px; text-align:right;">Total HT</th>
                </tr>
                {lignes_html}
            </table>
            <br><br>
            <table style="width:100%;">
                <tr>
                    <td style="width:60%;"></td>
                    <td style="width:40%; background:#FFF3E0; padding:15px; border-radius:5px;">
                        <table style="width:100%;">
                            <tr><td><b>Total HT :</b></td><td style="text-align:right;">{total_ht:.2f} €</td></tr>
                            <tr><td>TVA (20%) :</td><td style="text-align:right;">{total_ht*0.2:.2f} €</td></tr>
                            <tr style="font-size:18px; color:#FF4500;">
                                <td><b>TOTAL TTC :</b></td>
                                <td style="text-align:right;"><b>{total_ht*1.2:.2f} €</b></td>
                            </tr>
                        </table>
                    </td>
                </tr>
            </table>
        </div>
        """
        st.markdown(devis_template, unsafe_allow_html=True)

    else:
        st.title("🗄️ Archives des Devis")
        if not df_archives.empty:
            for nom in df_archives["Nom Devis"].unique():
                c1, c2 = st.columns([3, 1])
                c1.write(f"📁 **{nom}**")
                if c2.button("👁️ Ouvrir", key=nom):
                    st.session_state['devis_selectionne'] = nom
                    st.rerun()
        else:
            st.info("Aucun devis.")

# (Le reste du code pour les autres pages comme Nouveau Devis, Clients, etc. reste identique)
elif menu == "Nouveau Devis":
    st.title("📝 Nouveau Devis")
    df_c = pd.read_csv(CLIENTS_FILE)
    if df_c.empty:
        st.warning("Ajoutez un client.")
    else:
        client = st.selectbox("Client", df_c["Nom"].unique())
        art = st.text_input("Article")
        pa = st.number_input("Achat HT", min_value=0.0)
        co = st.number_input("Coeff", min_value=1.0, value=1.5)
        if st.button("🛒 AJOUTER"):
            pd.DataFrame([{"Client": client, "Article": art, "Vente HT": pa*co, "Marge": (pa*co)-pa}]).to_csv(PANIER_TEMP_FILE, mode='a', header=False, index=False)
            st.rerun()
        df_p = pd.read_csv(PANIER_TEMP_FILE)
        if not df_p.empty:
            st.table(df_p)
            n_d = st.text_input("Nom du devis")
            if st.button("💾 ARCHIVER"):
                df_p["Nom Devis"] = n_d
                df_p.to_csv(DEVIS_FILE, mode='a', header=False, index=False)
                pd.DataFrame(columns=["Client", "Article", "Vente HT", "Marge"]).to_csv(PANIER_TEMP_FILE, index=False)
                st.rerun()

elif menu == "Fiches Clients":
    st.title("👥 Clients")
    nom = st.text_input("Nom")
    if st.button("OK"):
        pd.DataFrame([{"Nom": nom, "Contact": ""}]).to_csv(CLIENTS_FILE, mode='a', header=False, index=False)
        st.rerun()
    st.table(pd.read_csv(CLIENTS_FILE))













