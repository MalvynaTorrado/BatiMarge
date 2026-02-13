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

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from datetime import datetime

# 1. Base de données simulée (Prix du Marché)
# Dans une version réelle, ces données viendraient d'une API comme Batiprix
PRIX_MARCHE = {
    "Placo BA13 (m²)": {"prix": 14.50, "unite": "m²"},
    "Isolant Laine de Roche (m²)": {"prix": 18.20, "unite": "m²"},
    "Peinture Acrylique (L)": {"prix": 22.00, "unite": "L"},
    "Parquet Chêne (m²)": {"prix": 55.00, "unite": "m²"}
}

def creer_pdf_devis(client, travaux, marge_artisan, taux_horaire, tva_taux=20):
    filename = f"Devis_{client.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.pdf"
    c = canvas.Canvas(filename, pagesize=A4)
    width, height = A4
    
    # --- Entête ---
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, height - 50, "VOTRE ENTREPRISE BTP")
    c.setFont("Helvetica", 10)
    c.drawString(50, height - 65, "123 Rue du Chantier, 75000 Paris")
    
    c.setFont("Helvetica-Bold", 12)
    c.drawString(350, height - 50, f"DEVIS POUR : {client}")
    c.drawString(350, height - 65, f"Date : {datetime.now().strftime('%d/%m/%Y')}")

    # --- Tableau des colonnes ---
    y = height - 120
    c.line(50, y+5, 550, y+5)
    c.drawString(50, y, "Désignation")
    c.drawString(200, y, "Qté")
    c.drawString(250, y, "Prix Marché")
    c.drawString(330, y, "Marge (%)")
    c.drawString(400, y, "Prix Final HT")
    c.line(50, y-5, 550, y-5)
    
    y -= 25
    total_ht = 0

    # --- Remplissage des lignes ---
    for item in travaux:
        nom = item['nom']
        qte = item['qte']
        temps_pose = item['heures_pose']
        
        # Récupération du prix marché
        p_base = PRIX_MARCHE.get(nom, {"prix": 0})["prix"]
        
        # Calcul : (Prix Marché + Marge) * Quantité + Main d'œuvre
        prix_avec_marge = p_base * (1 + marge_artisan / 100)
        total_ligne_materiaux = prix_avec_marge * qte
        total_mo = temps_pose * taux_horaire
        total_ligne_ht = total_ligne_materiaux + total_mo
        
        total_ht += total_ligne_ht

        # Écriture dans le PDF
        c.setFont("Helvetica", 9)
        c.drawString(50, y, nom)
        c.drawString(200, y, str(qte))
        c.drawString(250, y, f"{p_base}€")
        c.drawString(330, y, f"{marge_artisan}%")
        c.drawString(400, y, f"{total_ligne_ht:.2f} €")
        y -= 20

    # --- Totaux et TVA ---
    tva_montant = total_ht * (tva_taux / 100)
    total_ttc = total_ht + tva_montant

    y -= 40
    c.line(350, y+15, 550, y+15)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(350, y, f"TOTAL HT :")
    c.drawRightString(540, y, f"{total_ht:.2f} €")
    
    y -= 20
    c.setFont("Helvetica", 10)
    c.drawString(350, y, f"TVA ({tva_taux}%) :")
    c.drawRightString(540, y, f"{tva_montant:.2f} €")
    
    y -= 25
    c.setFont("Helvetica-Bold", 12)
    c.setFillColorRGB(0.1, 0.4, 0.1) # Vert pour le total
    c.drawString(350, y, "TOTAL TTC :")
    c.drawRightString(540, y, f"{total_ttc:.2f} €")

    c.save()
    print(f"Fichier créé : {filename}")

# --- Simulation d'un artisan réalisant un devis ---
mes_travaux = [
    {"nom": "Placo BA13 (m²)", "qte": 40, "heures_pose": 8},
    {"nom": "Peinture Acrylique (L)", "qte": 10, "heures_pose": 4}
]

# Paramètres : Client, Travaux, Marge (15%), Taux horaire (50€/h), TVA (10% pour rénovation)
creer_pdf_devis("M. Martin", mes_travaux, 15, 50, 10)







