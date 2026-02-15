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
