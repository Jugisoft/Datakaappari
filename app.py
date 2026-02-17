import streamlit as st
import pandas as pd

st.set_page_config(page_title="Pesis PRO-Analysaattori", layout="wide")

st.title("⚾ Pesis-Analysaattori (Excel & CSV Import)")

st.info("Lataa Power Queryllä haettu tiedosto (testi_1.xlsx tai events_.csv) tähän alapuolelle.")

uploaded_file = st.file_uploader("Valitse tiedosto", type=['csv', 'xlsx'])

if uploaded_file:
    try:
        # Automaattinen tunnistus tiedostopäätteen mukaan
        if uploaded_file.name.endswith('.xlsx'):
            df = pd.read_excel(uploaded_file)
        else:
            df = pd.read_csv(uploaded_file, sep=None, engine='python')
        
        st.success(f"Tiedosto luettu onnistuneesti! Tapahtumia: {len(df)}")

        # --- ANALYYSI OSA ---
        st.header("📊 Ottelun torjuntatilastot")
        
        # Tarkistetaan löytyykö tarvittavat sarakkeet
        needed_cols = ['pesat_teksti', 'tulos_teksti']
        if all(col in df.columns for col in needed_cols):
            
            # Lasketaan yritykset ja palot (torjunnat)
            summary = df.groupby('pesat_teksti').agg(
                Yritykset=('tulos_teksti', 'count'),
                Torjunnat=('tulos_teksti', lambda x: (x.astype(str).str.contains('Palo', case=False, na=False)).sum())
            ).reset_index()
            
            summary['Torjunta%'] = (summary['Torjunnat'] / summary['Yritykset'] * 100).round(1)
            
            # Järjestetään pesävälit loogisesti
            vali_jarjestys = {"0-1": 1, "1-2": 2, "2-3": 3, "3-Koti": 4}
            summary['order'] = summary['pesat_teksti'].map(vali_jarjestys)
            summary = summary.sort_values('order').drop('order', axis=1).fillna(0)
            
            st.table(summary)
            
        else:
            st.warning("Tiedostosta puuttuu sarakkeita. Varmista, että laajensit Power Queryssä kaikki kentät (lyoja_nimi, tulos_teksti jne.)")

        # --- LISÄTIEDOT ---
        with st.expander("Näytä raakadata"):
            st.dataframe(df)

    except Exception as e:
        st.error(f"Virhe tiedoston luvussa: {e}")
