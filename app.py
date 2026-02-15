import streamlit as st
import streamlit_authenticator as stauth
import pandas as pd
from fpdf import FPDF
from streamlit_drawable_canvas import st_canvas

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="BatiMarge Pro", page_icon="🏗️", layout="centered")

# --- 1. FONCTION GÉNÉRATION PDF (MISE À JOUR) ---
def generer_pdf(liste_materiaux, total_ht, tva_taux, user_info):
    pdf = FPDF()
    pdf.add_page()
    
    # En-tête Artisan
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 8, user_info['entreprise'], ln=True)
    pdf.set_font("Arial", '', 10)
    pdf.cell(0, 5, f"SIRET: {user_info['siret']}", ln=True)
    pdf.cell(0, 5, user_info['adresse'], ln=True)
    pdf.ln(10)

    # Titre
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, "DEVIS PROFESSIONNEL", ln=True, align='C')
    pdf.ln(5)

    # Tableau
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(90, 10, "Designation", border=1)
    pdf.cell(30, 10, "Quantite", border=1)
    pdf.cell(60, 10, "Total HT", border=1, ln=True)

    pdf.set_font("Arial", '', 10)
    for m in liste_materiaux:
        pdf.cell(90, 10, m['Matériau'], border=1)
        pdf.cell(30, 10, str(m['Quantité']), border=1)
        pdf.cell(60, 10, f"{m['Total HT']:.2f} €", border=1, ln=True)

    # Totaux
    pdf.ln(5)
    pdf.set_font("Arial", 'B', 11)
    pdf.cell(0, 8, f"Total HT : {total_ht:.2f} €", ln=True, align='R')
    pdf.cell(0, 8, f"TVA ({tva_taux*100}%) : {total_ht * tva_taux:.2f} €", ln=True, align='R')
    pdf.cell(0, 8, f"TOTAL TTC : {total_ht * (1 + tva_taux):.2f} €", ln=True, align='R')
    
    return pdf.output(dest='S').encode('latin-1')

# --- 2. CONFIGURATION DES IDENTIFIANTS ---
config = {
    'credentials': {
        'usernames': {
            'artisan1': {
                'email': 'contact@durand-renov.fr',
                'name': 'Jean Durand',
                'password': 'abc',  # Idéalement à hacher plus tard
                'entreprise': 'Durand Rénov SARL',
                'siret': '123 456 789 00012',
                'adresse': '12 rue de la Paix, 75000 Paris'
            }
        }
    },
    'cookie': {'expiry_days': 30, 'key': 'batimarge_secret', 'name': 'batimarge_cookie'}
}

authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days']
)

# --- 3. LOGIQUE D'AUTHENTIFICATION ---
authenticator.login(location='main', key='login_form')

if st.session_state["authentication_status"]:
    # TOUT LE CODE CI-DESSOUS EST ACCESSIBLE UNIQUEMENT SI CONNECTÉ
    authenticator.logout('Déconnexion', 'sidebar')
    user_info = config['credentials']['usernames'][st.session_state['username']]
    
    st.title(f"Espace {user_info['entreprise']}")
    st.write(f"Bonjour {st.session_state['name']}, préparez votre devis au juste prix.")

    # --- PARTIE MATÉRIAUX (Simulée pour l'exemple) ---
    st.header("1. Choix des matériaux")
    materiaux_dispos = {
        "Ciment 35kg": 12.50,
        "Plaque BA13": 9.20,
        "Rail Placo 3m": 5.40
    }
    
    selection = st.multiselect("Matériaux :", list(materiaux_dispos.keys()))
    devis_liste = []
    total_ht_materiaux = 0

    if selection:
        for item in selection:
            pu = materiaux_dispos[item]
            qte = st.number_input(f"Quantité pour {item}", min_value=1, value=1, key=f"qte_{item}")
            sous_total = pu * qte
            total_ht_materiaux += sous_total
            devis_liste.append({"Matériau": item, "Quantité": qte, "Total HT": sous_total})

        # --- TVA ET CALCULS ---
        st.header("2. Paramètres fiscaux")
        tva_options = {"Rénovation (5.5%)": 0.055, "Rénovation (10%)": 0.1, "Neuf (20%)": 0.2}
        choix_tva = st.selectbox("Taux de TVA :", list(tva_options.keys()))
        taux_tva = tva_options[choix_tva]

        # --- SIGNATURE ---
        st.header("3. Signature")
        canvas_result = st_canvas(stroke_width=2, stroke_color="#000", background_color="#eee", height=100, key="canvas")

        # --- GÉNÉRATION PDF ---
        if st.button("💾 Créer le Devis PDF"):
            pdf_data = generer_pdf(devis_liste, total_ht_materiaux, taux_tva, user_info)
            st.download_button(
                label="⬇️ Télécharger le Devis",
                data=pdf_data,
                file_name=f"Devis_{user_info['entreprise']}.pdf",
                mime="application/pdf"
            )

elif st.session_state["authentication_status"] is False:
    st.error('Identifiant ou mot de passe incorrect')
elif st.session_state["authentication_status"] is None:
    st.warning('Veuillez vous connecter pour accéder à l\'outil.')
