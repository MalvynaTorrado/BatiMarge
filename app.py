import streamlit as st
import pandas as pd

# --- MÉMOIRE DU DEVIS ---
if 'mon_devis' not in st.session_state:
    st.session_state['mon_devis'] = []
    
# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="BatiMarge Pro", layout="centered") # 'centered' fait moins vide sur PC

# --- STYLE CSS AVANCÉ (Les finitions) ---
st.markdown("""
    <style>
    /* Police et fond */
    html, body, [class*="css"]  {
        font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
    }
    .stApp { background-color: #F0F2F6; }

    /* Cartes blanches élégantes */
    div[data-testid="metric-container"] {
        background-color: white;
        padding: 25px;
        border-radius: 20px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.05);
        border: none;
        text-align: center;
    }
    
    /* Titres plus modernes */
    h1 { color: #1E1E1E; font-weight: 800 !important; }
    
    /* Bouton d'action arrondi et coloré */
    .stButton>button {
        width: 100%;
        background: linear-gradient(135deg, #FF8C00 0%, #FF4500 100%);
        color: white;
        border-radius: 12px;
        border: none;
        padding: 15px;
        font-size: 18px;
        font-weight: bold;
        transition: 0.3s;
        box-shadow: 0 4px 15px rgba(255, 140, 0, 0.3);
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(255, 140, 0, 0.4);
    }

    /* Input (cases de saisie) plus douces */
    .stTextInput>div>div>input, .stNumberInput>div>div>input {
        border-radius: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- BARRE LATÉRALE ---
with st.sidebar:
    try:
        st.image("logo.png", width=180)
    except:
        st.title("🏗️ BatiMarge")
    
    st.markdown("---")
    menu = st.radio("MENU PRINCIPAL", ["Tableau de bord", "Calculateur Devis", "Scan-Marge"])
    st.markdown("---")
    st.caption("Version 1.2 Pro")

# --- TABLEAU DE BORD ---
if menu == "Tableau de bord":
    st.title("Tableau de bord")
    st.write("Suivi de votre rentabilité en temps réel.")
    
    m1, m2 = st.columns(2)
    with m1:
        st.metric("Chantiers en cours", "8")
    with m2:
        st.metric("Marge globale", "32.5%")
    
    st.markdown("### Dernières opérations")
    # Simulation d'un petit tableau propre
    data = {"Client": ["Dumont", "SARL Batir", "Leclerc"], "Marge (€)": [450, 1200, 890]}
    st.table(pd.DataFrame(data))

# --- CALCULATEUR ---
elif menu == "Calculateur Devis":
    st.title("📝 Nouveau Calcul")
    
    with st.expander("👤 Informations Client", expanded=True):
        col1, col2 = st.columns(2)
        client = col1.text_input("Nom du client")
        chantier = col2.text_input("Référence chantier")

    with st.container():
        st.markdown("### Détail du produit")
        c1, c2, c3 = st.columns([2, 1, 1])
        article = c1.text_input("Matériau / Article")
        p_achat = c2.number_input("Achat HT", min_value=0.0)
        coeff = c3.number_input("Coeff.", min_value=1.0, value=1.5, step=0.1)
        
        p_vente = p_achat * coeff
        marge = p_vente - p_achat
        
        st.markdown(f"""
        <div style="background-color:#FFF3E0; padding:20px; border-radius:15px; border-left: 5px solid #FF8C00;">
            <p style="margin:0; color:#E65100; font-size:14px;">PRIX DE VENTE CONSEILLÉ</p>
            <h2 style="margin:0; color:#E65100;">{p_vente:.2f} € HT</h2>
            <p style="margin:0; color:#555;">Bénéfice net : {marge:.2f} €</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.write("") # Espace
        if st.button("ENREGISTRER L'ARTICLE"):
            st.success("Ajouté avec succès au devis !")

# --- SCANNER ---
elif menu == "Scan-Marge":
    st.title("📸 Scanner")
    st.write("Prenez une photo d'une étiquette ou d'un devis fournisseur.")
    st.camera_input("Capturez le document")

import streamlit as st
from streamlit_drawable_canvas import st_canvas
from PIL import Image
import numpy as np

def module_signature(nom_client):
    st.subheader("✍️ Validation et Signature")
    st.write(f"Signature demandée pour accord du devis par : **{nom_client}**")
    
    # Création de la zone de dessin (Canvas)
    canvas_result = st_canvas(
        fill_color="rgba(255, 255, 255, 1)",  # Fond blanc
        stroke_width=3,                       # Épaisseur du trait
        stroke_color="#000000",               # Couleur de l'encre (Noir)
        background_color="#F0F2F6",           # Couleur de fond du cadre (Gris clair)
        height=200,                           # Hauteur adaptée aux mobiles
        width=350,                            # Largeur adaptée aux mobiles
        drawing_mode="freedraw",              # Mode dessin libre
        key="canvas_signature",
    )

    # Si le client a dessiné quelque chose et clique sur "Valider"
    if canvas_result.image_data is not None:
        if st.button("✅ Confirmer la commande"):
            # L'image est un tableau mathématique (numpy array), on la convertit en vraie image
            img_data = canvas_result.image_data.astype(np.uint8)
            image_signature = Image.fromarray(img_data, 'RGBA')
            
            # Sauvegarde de la signature sous forme de fichier image
            chemin_signature = f"signature_{nom_client.replace(' ', '_')}.png"
            image_signature.save(chemin_signature)
            
            st.success("Devis signé et validé avec succès ! 🎉")
            st.balloons() # Petite animation sympa pour fêter la vente
            
            return chemin_signature
            
    return None

# --- TEST DANS L'APPLICATION ---
# chemin_fichier = module_signature("M. Dupont")


