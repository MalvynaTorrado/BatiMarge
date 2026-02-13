import streamlit as st
import pandas as pd
import os

# --- 1. CONFIGURATION ET INITIALISATION DES FICHIERS ---
st.set_page_config(page_title="BatiMarge Expert", layout="centered")

CLIENTS_FILE = "clients.csv"
DEVIS_FILE = "devis_archives.csv"

# Cette fonction prépare tes "étagères" (fichiers) pour qu'elles ne soient jamais vides
def initialiser_systeme():
    if not os.path.exists(CLIENTS_FILE) or os.stat(CLIENTS_FILE).st_size == 0:
        pd.DataFrame(columns=["Nom", "Contact"]).to_csv(CLIENTS_FILE, index=False)
    if not os.path.exists(DEVIS_FILE) or os.stat(DEVIS_FILE).st_size == 0:
        pd.DataFrame(columns=["Client", "Article", "Achat HT", "Vente HT", "Marge", "Nom Devis"]).to_csv(DEVIS_FILE, index=False)

initialiser_systeme()

# Mémoire vive pour garder tes articles tant que tu ne fermes pas l'appli
if 'panier' not in st.session_state:
    st.session_state['panier'] = []

# --- 2. DESIGN PERSONNALISÉ (CSS) ---
st.markdown("""
    <style>
    .stApp { background-color: #F8F9FA; }
    /* Style des boutons */
    .stButton>button {
        width: 100%; background: linear-gradient(135deg, #FF8C00 0%, #FF4500 100%);
        color: white; border-radius: 12px; border: none; font-weight: bold; padding: 12px;
        box-shadow: 0 4px 10px rgba(255, 69, 0, 0.3);
    }
    /* Style des cartes de stats */
    div[data-testid="metric-container"] {
        background-color: white; padding: 20px; border-radius: 15px; box-shadow: 0 4px 10px rgba(0,0,0,0.05);
    }
    /* Encadré du résultat de vente */
    .result-box {
        background-color:#FFF3E0; padding:20px; border-radius:15px; border-left: 5px solid #FF8C00; margin-top:10px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. BARRE LATÉRALE (MENU) ---
with st.sidebar:
    try:
        st.image("logo.png", width=180)
    except:
        st.title("🏗️ BatiMarge")
    
    st.divider()
    menu = st.radio("NAVIGATION", ["Tableau de bord", "Fiches Clients", "Calculateur", "Mon Devis en cours", "Archives"])
    st.divider()
    st.caption("Version 2.0 - Expert Artisan")

# --- 4. LOGIQUE DES PAGES ---

# --- PAGE 1 : TABLEAU DE BORD ---
if menu == "Tableau de bord":
    st.title("Tableau de bord 👋")
    col1, col2 = st.columns(2)
    
    # On compte les clients
    df_c = pd.read_csv(CLIENTS_FILE)
    nb_clients = len(df_c)
    
    # On calcule le panier actuel
    total_panier = sum(item['Vente HT'] for item in st.session_state['panier'])
    
    col1.metric("Total Clients", nb_clients)
    col2.metric("Panier en cours HT", f"{total_panier:.2f} €")
    
    st.info("Sélectionnez une option dans le menu à gauche pour commencer.")

# --- PAGE 2 : GESTION CLIENTS ---
elif menu == "Fiches Clients":
    st.title("👥 Gestion des Clients")
    
    with st.expander("➕ Enregistrer un nouveau client"):
        nom_c = st.text_input("Nom de l'entreprise ou du particulier")
        tel_c = st.text_input("N° de téléphone / Email")
        if st.button("Valider la création"):
            if nom_c:
                nouveau = pd.DataFrame([{"Nom": nom_c, "Contact": tel_c}])
                nouveau.to_csv(CLIENTS_FILE, mode='a', header=False, index=False)
                st.success(f"Client '{nom_c}' enregistré avec succès !")
                st.rerun()
            else:
                st.error("Le nom est obligatoire.")

    st.subheader("Répertoire Clients")
    df_c = pd.read_csv(CLIENTS_FILE)
    if not df_c.empty:
        st.dataframe(df_c, use_container_width=True)
    else:
        st.info("Votre répertoire est vide.")

# --- PAGE 3 : CALCULATEUR ---
elif menu == "Calculateur":
    st.title("📝 Chiffrage Rapide")
    df_clients = pd.read_csv(CLIENTS_FILE)
    
    if df_clients.empty:
        st.warning("⚠️ Allez dans 'Fiches Clients' pour créer votre premier client.")
    else:
        client_choisi = st.selectbox("Pour quel client ?", df_clients["Nom"].unique())
        
        with st.container():
            art = st.text_input("Désignation de l'article (ex: Carrelage 60x60)")
            c1, c2 = st.columns(2)
            p_achat = c1.number_input("Prix Achat HT (€)", min_value=0.0, step=1.0)
            coeff = c2.number_input("Coefficient", min_value=1.0, value=1.5, step=0.1)
            
            p_vente = p_achat * coeff
            marge = p_vente - p_achat
            
            st.markdown(f"""
            <div class="result-box">
                <p style="margin:0; color:#E65100; font-size:14px;">PRIX DE VENTE CONSEILLÉ</p>
                <h2 style="margin:0; color:#E65100;">{p_vente:.2f} € HT</h2>
                <p style="margin:0; color:#555;">Marge nette : {marge:.2f} €</p>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("🛒 AJOUTER AU DEVIS"):
                if art:
                    st.session_state['panier'].append({
                        "Client": client_choisi, "Article": art, "Achat HT": p_achat, "Vente HT": p_vente, "Marge": marge
                    })
                    st.success("Article ajouté au devis en cours !")
                else:
                    st.error("Donnez un nom à l'article.")

# --- PAGE 4 : PANIER (MON DEVIS) ---
elif menu == "Mon Devis en cours":
    st.title("📂 Devis en préparation")
    if st.session_state['panier']:
        df_p = pd.DataFrame(st.session_state['panier'])
        st.table(df_p)
        
        total_devis = df_p["Vente HT"].sum()
        st.subheader(f"Total Général HT : {total_devis:.2f} €")
        
        nom_archive = st.text_input("Nom du devis pour archive (ex: Chantier Dupont Cuisine)")
        if st.button("💾 ARCHIVER CE DEVIS"):
            if nom_archive:
                df_p["Nom Devis"] = nom_archive
                df_p.to_csv(DEVIS_FILE, mode='a', header=False, index=False)
                st.session_state['panier'] = []
                st.success("Devis enregistré dans les archives !")
                st.rerun()
            else:
                st.error("Veuillez nommer ce devis avant d'archiver.")
    else:
        st.info("Le devis actuel est vide. Utilisez le Calculateur.")

# --- PAGE 5 : ARCHIVES ---
elif menu == "Archives":
    st.title("🗄️ Archives des Devis")
    if os.path.exists(DEVIS_FILE):
        df_a = pd.read_csv(DEVIS_FILE)
        if not df_a.empty:
            liste_devis = df_a["Nom Devis"].unique()
            choix_devis = st.selectbox("Ouvrir un devis archivé", liste_devis)
            
            recap = df_a[df_a["Nom Devis"] == choix_devis]
            st.table(recap)
            st.write(f"**Total HT : {recap['Vente HT'].sum():.2f} €**")
            
            if st.button("🗑️ Vider TOUTES les archives"):
                os.remove(DEVIS_FILE)
                st.rerun()
        else:
            st.info("Aucune archive trouvée.")







