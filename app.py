import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# --- CONFIGURATION ET BDD ---
st.set_page_config(page_title="Artisan Devis Pro", layout="wide")

def init_db():
    conn = sqlite3.connect('artisan.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS devis 
                 (id INTEGER PRIMARY KEY, client TEXT, date TEXT, total_ht REAL, marge REAL)''')
    conn.commit()
    conn.close()

init_db()

# --- DONNÉES PRIX DU MARCHÉ ---
PRIX_MARCHE = {
    "Peinture Velours (L)": 22.50,
    "Placo BA13 (m²)": 14.80,
    "Sac de Ciment (35kg)": 8.90,
    "Carrelage Grès Cérame (m²)": 35.00
}

# --- INTERFACE ---
st.title("🏗️ Générateur de Devis au Juste Prix")

col1, col2 = st.columns([1, 1])

with col1:
    st.header("1. Détails du Devis")
    nom_client = st.text_input("Nom du Client")
    marge = st.slider("Votre Marge sur Matériaux (%)", 0, 50, 20)
    taux_horaire = st.number_input("Votre Taux Horaire (€/h)", value=45)
    
    st.subheader("Articles à ajouter")
    article = st.selectbox("Choisir un matériau (Prix Marché)", list(PRIX_MARCHE.keys()))
    qte = st.number_input("Quantité", min_value=1, value=1)
    heures = st.number_input("Temps de pose (heures)", min_value=0.0, value=1.0)
    
    if st.button("Ajouter au devis"):
        if 'panier' not in st.session_state:
            st.session_state.panier = []
        
        prix_base = PRIX_MARCHE[article]
        prix_vente = prix_base * (1 + marge/100)
        total_ligne = (prix_vente * qte) + (heures * taux_horaire)
        
        st.session_state.panier.append({
            "Désignation": article,
            "Qté": qte,
            "Prix Marché": f"{prix_base}€",
            "Prix HT (Marge incl.)": f"{total_ligne:.2f}€"
        })

with col2:
    st.header("2. Récapitulatif")
    if 'panier' in st.session_state and st.session_state.panier:
        df = pd.DataFrame(st.session_state.panier)
        st.table(df)
        
        # Calcul du Total
        total_final = sum([float(x.replace('€', '')) for x in df["Prix HT (Marge incl.)"]])
        st.metric("TOTAL DEVIS HT", f"{total_final:.2f} €")
        
        if st.button("Enregistrer le Devis"):
            conn = sqlite3.connect('artisan.db')
            c = conn.cursor()
            c.execute("INSERT INTO devis (client, date, total_ht, marge) VALUES (?, ?, ?, ?)", 
                      (nom_client, datetime.now().strftime("%d/%m/%Y"), total_final, marge))
            conn.commit()
            conn.close()
            st.success("Devis enregistré avec succès !")
    else:
        st.info("Ajoutez des articles pour commencer le chiffrage.")

# --- HISTORIQUE ---
st.divider()
st.header("📜 Historique des Devis")
conn = sqlite3.connect('artisan.db')
historique_df = pd.read_sql_query("SELECT * FROM devis ORDER BY id DESC", conn)
st.dataframe(historique_df, use_container_width=True)
conn.close()






