import streamlit as st
import pandas as pd

st.set_page_config(page_title="Pesis PRO: Tilastoanalyysi", layout="wide")

st.title("⚾ Pesis-Analysaattori PRO")
st.markdown("---")

uploaded_file = st.file_uploader("Lataa laajennettu Excel tai CSV", type=['csv', 'xlsx'])

if uploaded_file:
    try:
        # Lukeminen
        if uploaded_file.name.endswith('.xlsx'):
            df = pd.read_excel(uploaded_file)
        else:
            df = pd.read_csv(uploaded_file)
            
        st.success(f"Data ladattu! Rivimäärä laajennuksen jälkeen: {len(df)}")

        # --- 1. TORJUNTAPROSENTIT PESÄVÄLEITTÄIN ---
        st.header("🛡️ Ulkopelin torjuntatehokkuus")
        
        if 'pesat_teksti' in df.columns and 'tulos_teksti' in df.columns:
            # Siivotaan data: poistetaan tyhjät ja "Vapaa" -tyyppiset, jotka eivät ole varsinaisia suorituksia
            df_clean = df[df['pesat_teksti'].notna()].copy()
            
            # Ryhmittely
            summary = df_clean.groupby('pesat_teksti').agg(
                Yritykset=('tulos_teksti', 'count'),
                Palot=('tulos_teksti', lambda x: x.astype(str).str.contains('Palo', case=False).sum()),
                Juoksut=('tulos_teksti', lambda x: x.astype(str).str.contains('Juoksu', case=False).sum())
            ).reset_index()
            
            # Lasketaan Torjunta% (Palot / Yritykset)
            summary['Torjunta%'] = (summary['Palot'] / summary['Yritykset'] * 100).round(1)
            
            # Järjestys
            jarjestys = {"0-1": 1, "1-2": 2, "2-3": 3, "3-Koti": 4}
            summary['sort'] = summary['pesat_teksti'].map(jarjestys)
            summary = summary.sort_values('sort').drop('sort', axis=1).fillna(0)
            
            st.table(summary)
            
        # --- 2. LYÖNTISUUNTA JA TULOS ---
        st.header("🎯 Lyöntianalyysi")
        col1, col2 = st.columns(2)
        
        with col1:
            if 'lyonni_suunta' in df.columns:
                st.subheader("Suosituimmat lyöntisuunnat")
                st.bar_chart(df['lyonni_suunta'].value_counts())
        
        with col2:
            if 'lyonni_laji' in df.columns:
                st.subheader("Lyöntityypit")
                st.write(df['lyonni_laji'].value_counts())

        # --- 3. PELAAJAKOHTAINEN ETSIN ---
        st.header("🔍 Pelaajakohtainen tarkastelu")
        pelaaja = st.selectbox("Valitse lyöjä:", options=df['lyoja_nimi'].unique())
        pelaaja_df = df[df['lyoja_nimi'] == pelaaja]
        st.dataframe(pelaaja_df[['lyoja_numero', 'pesat_teksti', 'lyonni_suunta', 'tulos_teksti']])

    except Exception as e:
        st.error(f"Virhe analyysissa: {e}")
else:
    st.info("Pudota yläpuolelle se Excel-tiedosto, jonka sait Power Querysta ulos.")
