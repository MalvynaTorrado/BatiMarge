import streamlit as st
import pandas as pd
import os
from datetime import datetime
import streamlit as st
import pandas as pd
import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader

# 1. Définition des utilisateurs (Identifiant / Nom / Mot de passe haché)
# Note : En production, on utilise des mots de passe hachés pour la sécurité
config = {
    'credentials': {
        'usernames': {
            'artisan1': {
                'email': 'contact@artisan.fr',
                'name': 'Jean Durand',
                'password': 'abc' # À remplacer par un hash plus tard
            }
        }
    },
    'cookie': {
        'expiry_days': 30,
        'key': 'some_signature_key',
        'name': 'artisan_auth_cookie'
    }
}

authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days']
)

# 2. Affichage du formulaire de connexion
name, authentication_status, username = authenticator.login('Connexion', 'main')

if authentication_status:
    # --- SI L'ARTISAN EST CONNECTÉ ---
    authenticator.logout('Déconnexion', 'sidebar')
    st.write(f'Bienvenue, **{name}** !')
    
    # ICI : Tout ton code précédent (calculs, PDF, etc.)
    
elif authentication_status == False:
    st.error('Identifiant ou mot de passe incorrect')
elif authentication_status == None:
    st.warning('Veuillez entrer votre identifiant et mot de passe')
def check_password():
    password = st.text_input("Mot de passe", type="password")
    if password == st.secrets["password"]:
        return True
    return False

if not check_password():
    st.stop() # Arrête l'exécution si le mot de passe est faux
# "https://docs.google.com/spreadsheets/d/e/2PACX-1vQSQjxU9E4qrkgukQutzuHtuIUcEhAjEUitVoe8eK96uRV7z4YiPzIfHqYyX586wNvfsbhF0x8o-MYf/pubhtml"

# Fonction pour charger les données avec mise à jour automatique
@st.cache_data(ttl=600) # Rafraîchit les données toutes les 10 minutes
def load_data():
    return pd.read_csv(SHEET_URL)

try:
    df_materiaux = load_data()
    st.sidebar.success("✅ Prix du marché mis à jour")
except:
    st.sidebar.error("⚠️ Erreur de connexion aux prix")
    # Backup au cas où la connexion échoue
    df_materiaux = pd.DataFrame({"Matériau": ["Exemple"], "Prix Unitaire HT": [0.0], "Unité": ["-"]})
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
from streamlit_drawable_canvas import st_canvas

st.header("3. Signature du client")
canvas_result = st_canvas(
    fill_color="rgba(255, 165, 0, 0.3)",  # Couleur de remplissage
    stroke_width=3,
    stroke_color="#000000",
    background_color="#eee",
    height=150,
    drawing_mode="freedraw",
    key="canvas",
)
from fpdf import FPDF

def generer_pdf(donnees_devis, total_ht, logo_path):
    pdf = FPDF()
    pdf.add_page()
    
    # 1. Ajout du Logo
    try:
        pdf.image(logo_path, x=10, y=8, w=33)
    except:
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(0, 10, "MON ENTREPRISE", ln=True)

    pdf.ln(20) # Saut de ligne

    # 2. Titre du Devis
    pdf.set_font("Arial", 'B', 20)
    pdf.cell(0, 10, "DEVIS PREVISIONNEL", ln=True, align='C')
    pdf.ln(10)

    # 3. Tableau des matériaux
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(90, 10, "Designation", border=1)
    pdf.cell(30, 10, "Qté", border=1)
    pdf.cell(30, 10, "PU HT", border=1)
    pdf.cell(40, 10, "Total HT", border=1, ln=True)

    pdf.set_font("Arial", '', 12)
    for item in donnees_devis:
        pdf.cell(90, 10, item['Matériau'], border=1)
        pdf.cell(30, 10, str(item['Quantité']), border=1)
        pdf.cell(30, 10, "-", border=1) # On pourrait ajouter le PU ici
        pdf.cell(40, 10, f"{item['Total HT']:.2f} €", border=1, ln=True)

    pdf.ln(10)
    
    # 4. Total Final
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, f"TOTAL GENERAL HT : {total_ht:.2f} EUR", ln=True, align='R')
    
    return pdf.output(dest='S').encode('latin-1') # Retourne le PDF en binaire
if st.button("💾 Finaliser et Télécharger le PDF"):
    pdf_bin = generer_pdf(devis_liste, total_final_ht, "logo.png")
    
    st.download_button(
        label="Cliquer ici pour télécharger le devis",
        data=pdf_bin,
        file_name="devis_artisan.pdf",
        mime="application/pdf"
    )
# Choix du taux de TVA
st.header("3. Paramètres fiscaux")
type_travaux = st.selectbox(
    "Type de travaux :",
    ["Rénovation énergétique (5.5%)", "Rénovation classique (10%)", "Neuf / Divers (20%)"]
)

# Dictionnaire de correspondance
tva_map = {"Rénovation énergétique (5.5%)": 0.055, "Rénovation classique (10%)": 0.1, "Neuf / Divers (20%)": 0.2}
taux_tva = tva_map[type_travaux]

# Calculs finaux mis à jour
montant_tva = total_final_ht * taux_tva
total_ttc = total_final_ht + montant_tva

st.metric("Total HT", f"{total_final_ht:.2f} €")
st.metric(f"TVA ({taux_tva*100}%)", f"{montant_tva:.2f} €")
st.success(f"### TOTAL TTC : {total_ttc:.2f} €")







