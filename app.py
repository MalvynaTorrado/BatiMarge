<th style="padding:10px; text-align:left;">Désignation</th>
                    <th style="padding:10px; text-align:right;">Total HT</th>
                </tr>
                {lignes_html}
            </table>
            <br><br>
            <table style="width:100%;">
                <tr>
                    <td style="width:60%;"></td>
                    <td style="width:40%; background:#FFF3E0; padding:15px; border-radius:5px;">
                        <table style="width:100%;">
                            <tr><td><b>Total HT :</b></td><td style="text-align:right;">{total_ht:.2f} €</td></tr>
                            <tr><td>TVA (20%) :</td><td style="text-align:right;">{total_ht*0.2:.2f} €</td></tr>
                            <tr style="font-size:18px; color:#FF4500;">
                                <td><b>TOTAL TTC :</b></td>
                                <td style="text-align:right;"><b>{total_ht*1.2:.2f} €</b></td>
                            </tr>
                        </table>
                    </td>
                </tr>
            </table>
        </div>
        """
        st.markdown(devis_template, unsafe_allow_html=True)

    else:
        st.title("🗄️ Archives des Devis")
        if not df_archives.empty:
            for nom in df_archives["Nom Devis"].unique():
                c1, c2 = st.columns([3, 1])
                c1.write(f"📁 **{nom}**")
                if c2.button("👁️ Ouvrir", key=nom):
                    st.session_state['devis_selectionne'] = nom
                    st.rerun()
        else:
            st.info("Aucun devis.")

# (Le reste du code pour les autres pages comme Nouveau Devis, Clients, etc. reste identique)
elif menu == "Nouveau Devis":
    st.title("📝 Nouveau Devis")
    df_c = pd.read_csv(CLIENTS_FILE)
    if df_c.empty:
        st.warning("Ajoutez un client.")
    else:
        client = st.selectbox("Client", df_c["Nom"].unique())
        art = st.text_input("Article")
        pa = st.number_input("Achat HT", min_value=0.0)
        co = st.number_input("Coeff", min_value=1.0, value=1.5)
        if st.button("🛒 AJOUTER"):
            pd.DataFrame([{"Client": client, "Article": art, "Vente HT": pa*co, "Marge": (pa*co)-pa}]).to_csv(PANIER_TEMP_FILE, mode='a', header=False, index=False)
            st.rerun()
        df_p = pd.read_csv(PANIER_TEMP_FILE)
        if not df_p.empty:
            st.table(df_p)
            n_d = st.text_input("Nom du devis")
            if st.button("💾 ARCHIVER"):
                df_p["Nom Devis"] = n_d
                df_p.to_csv(DEVIS_FILE, mode='a', header=False, index=False)
                pd.DataFrame(columns=["Client", "Article", "Vente HT", "Marge"]).to_csv(PANIER_TEMP_FILE, index=False)
                st.rerun()

elif menu == "Fiches Clients":
    st.title("👥 Clients")
    nom = st.text_input("Nom")
    if st.button("OK"):
        pd.DataFrame([{"Nom": nom, "Contact": ""}]).to_csv(CLIENTS_FILE, mode='a', header=False, index=False)
        st.rerun()
    st.table(pd.read_csv(CLIENTS_FILE))












