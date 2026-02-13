import streamlit as st
import pandas as pd

# --- 1. CONFIGURATION ET MÉMOIRE ---
st.set_page_config(page_title="BatiMarge Pro", layout="centered")

# Cette partie crée la mémoire pour stocker tes articles
if 'mon_devis' not in st.session_state:
    st.session_state['mon_devis'] = []

# --- 2. STYLE DESIGN (Finitions) ---
st.markdown("""
    <style>
    .stApp { background-color: #F8F9FA; }
    .stButton>button {
        width: 100%; background: linear-gradient(135deg, #FF8C00 0%, #FF4500 100%);
        color: white; border-radius: 12px; border: none; font-weight: bold; padding: 15px;
    }
    div[data-testid="metric-container"] {
        background-color: white; padding: 20px; border-radius: 15px; box-shadow: 0 4px 10px rgba(0,0,0,0.05);
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
    menu = st.radio("MENU PRINCIPAL", [
        "Tableau de bord", 
        "Calculateur", 
        "Consulter mon Devis", 
        "Scan-Marge"
    ])
    st.divider()
    st.caption("Application Artisan Pro v1.5")

# --- 4. LOGIQUE DES PAGES ---

# --- PAGE : TABLEAU DE BORD ---
if menu == "Tableau de bord":
    st.title("Tableau de bord")
    col1, col2 = st.columns(2)
    total_articles = len(st.session_state['mon_devis'])
    total_devis = sum(item['Prix Vente HT'] for item in st.session_state['mon_devis'])
    
    col1.metric("Articles enregistrés", total_articles)
    col2.metric("Total Devis HT", f"{total_devis:.2f} €")
    st.write("Bienvenue sur votre outil de gestion de marge.")

# --- PAGE : CALCULATEUR ---
elif menu == "Calculateur":
    st.title("📝 Nouveau Calcul")
    
    with st.container():
        art = st.text_input("Désignation du matériau (ex: Sac de ciment)")
        c1, c2 = st.columns(2)
        p_achat = c1.number_input("Prix Achat HT (€)", min_value=0.0, step=0.1)
        coeff = c2.number_input("Coefficient de marge", min_value=1.0, value=1.5, step=0.1)
        
        p_vente = p_achat * coeff
        marge = p_vente - p_achat
        
        # Affichage du résultat en grand
        st.markdown(f"""
        <div style="background-color:#FFF3E0; padding:20px; border-radius:15px; border-left: 5px solid #FF8C00; margin-bottom:20px;">
            <p style="margin:0; color:#E65100; font-size:14px;">PRIX DE VENTE CONSEILLÉ</p>
            <h2 style="margin:0; color:#E65100;">{p_vente:.2f} € HT</h2>
            <p style="margin:0; color:#555;">Bénéfice : {marge:.2f} €</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("💾 ENREGISTRER DANS LE DEVIS"):
            if art != "":
                # On ajoute les données dans la mémoire
                st.session_state['mon_devis'].append({
                    "Article": art,
                    "Prix Achat HT": p_achat,
                    "Coeff": coeff,
                    "Prix Vente HT": p_vente,
                    "Marge (€)": marge
                })
                st.success(f"L'article '{art}' a été ajouté au devis !")
            else:
                st.error("Veuillez entrer un nom pour l'article.")

# --- PAGE : CONSULTER MON DEVIS ---
elif menu == "Consulter mon Devis":
    st.title("📂 Récapitulatif du Devis")
    
    if len(st.session_state['mon_devis']) > 0:
        # On transforme la mémoire en tableau
        df = pd.DataFrame(st.session_state['mon_devis'])
        st.table(df) # Affichage propre du tableau
        
        total_ht = df["Prix Vente HT"].sum()
        total_marge = df["Marge (€)"].sum()
        
        st.divider()
        st.subheader(f"Total Général HT : {total_ht:.2f} €")
        st.success(f"Marge totale sur ce chantier : {total_marge:.2f} €")
        
        if st.button("🗑️ TOUT EFFACER"):
            st.session_state['mon_devis'] = []
            st.rerun()
    else:
        st.warning("Votre devis est vide pour le moment.")

# --- PAGE : SCAN-MARGE ---
elif menu == "Scan-Marge":
    st.title("📸 Scanner")
    st.camera_input("Scanner une étiquette ou un document")



