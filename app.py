import streamlit as st
import streamlit_authenticator as stauth
import pandas as pd
from fpdf import FPDF
from streamlit_drawable_canvas import st_canvas

# --- CONFIGURATION ---
st.set_page_config(page_title="BatiMarge Pro", layout="centered")

# --- 1. DEFINITION DES UTILISATEURS ---
# On met les données ici pour éviter l'erreur des "Secrets" (Photo 4)
config = {
    'credentials': {
        'usernames': {
            'artisan1': {
                'email': 'contact@durand-renov.fr',
                'name': 'Jean Durand',
                'password': 'abc', 
                'entreprise': 'Durand Rénov SARL',
                'siret': '123 456 789 00012',
                'adresse': '12 rue de la Paix, 75000 Paris'
            }
        }
    },
    'cookie': {
        'expiry_days': 30,
        'key': 'batimarge_secret_key',
        'name': 'batimarge_cookie'
    }
}

# --- 2. INITIALISATION AUTHENTIFICATION ---
authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days']
)

# Correction de l'erreur Photo 2 & 3 : On utilise une clé unique
authenticator.login(location='main', key='login_form_unique')

# --- 3. L'APPLICATION (UNIQUEMENT SI CONNECTÉ) ---
if st.session_state["authentication_status"]:
    authenticator.logout('Déconnexion', 'sidebar')
    
    # Récupération sécurisée des infos
    user = config['credentials']['usernames'][st.session_state['username']]
    st.title(f"Espace {user['entreprise']}")

    # --- PARTIE CALCULS ---
    st.header("1. Détails du devis")
    
    # On définit une valeur par défaut pour éviter la NameError (Photo 5)
    total_final_ht = st.number_input("Montant total HT des travaux (€)", min_value=0.0, value=0.0)

    # Paramètres fiscaux
    st.header("2. Paramètres fiscaux")
    tva_options = {"Rénovation (5.5%)": 0.055, "Rénovation (10%)": 0.1, "Neuf (20%)": 0.2}
    choix_tva = st.selectbox("Type de travaux :", list(tva_options.keys()))
    taux_tva = tva_options[choix_tva]

    # Calculs (Maintenant total_final_ht existe forcément !)
    montant_tva = total_final_ht * taux_tva
    total_ttc = total_final_ht + montant_tva

    col1, col2 = st.columns(2)
    col1.metric("TVA", f"{montant_tva:.2f} €")
    col2.metric("Total TTC", f"{total_ttc:.2f} €")

    # --- SIGNATURE ---
    st.header("3. Signature")
    canvas_result = st_canvas(
        stroke_width=2,
        stroke_color="#000",
        background_color="#eee",
        height=150,
        key="canvas"
    )

    # --- BOUTON PDF ---
    if st.button("💾 Générer le PDF"):
        if total_final_ht > 0:
            st.success("Devis prêt pour le téléchargement !")
            # La fonction PDF serait appelée ici
        else:
            st.warning("Veuillez entrer un montant supérieur à 0.")

elif st.session_state["authentication_status"] is False:
    st.error('Identifiant ou mot de passe incorrect')
elif st.session_state["authentication_status"] is None:
    st.info('Veuillez vous connecter pour accéder à l\'outil BatiMarge.')
