import streamlit as st

# Configuration de l'interface
st.title("Calculateur de Devis Artisan")

# 1. Paramètres de l'artisan
st.sidebar.header("Vos Tarifs")
taux_horaire = st.sidebar.number_input("Taux horaire (€/h)", value=45.0)
marge_materiaux = st.sidebar.slider("Marge sur matériaux (%)", 0, 100, 20) / 100

# 2. Base de données fictive (Simulant une API)
base_prix = {
    "Placo BA13 (m2)": 12.50,
    "Peinture Velours (L)": 18.00,
    "Sac de Ciment 35kg": 7.50
}

# 3. Sélection des matériaux
st.subheader("Choix des matériaux")
article = st.selectbox("Sélectionner un matériau", list(base_prix.keys()))
quantite = st.number_input("Quantité", min_value=1.0, value=1.0)
temps_pose = st.number_input("Temps de pose estimé (heures)", min_value=0.5, value=1.0)

# 4. Calculs mathématiques
prix_achat = base_prix[article] * quantite
prix_vente_mat = prix_achat * (1 + marge_materiaux)
cout_mo = temps_pose * taux_horaire
total_ht = prix_vente_mat + cout_mo

# 5. Affichage du résultat
st.divider()
st.write(f"### Total Devis HT : **{total_ht:.2f} €**")
st.write(f"*Matériaux (avec marge) : {prix_vente_mat:.2f} €*")
st.write(f"*Main d'œuvre : {cout_mo:.2f} €*")








