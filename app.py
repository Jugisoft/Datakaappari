import streamlit as st
import pandas as pd

st.set_page_config(page_title="Pesis PRO: Lukkari & Tilanne-analyysi", layout="wide")

st.title("⚾ Pesis-Analysaattori PRO")
st.markdown("---")

uploaded_file = st.file_uploader("Lataa laajennettu Excel tai CSV", type=['csv', 'xlsx'])

if uploaded_file:
    try:
        # Tiedoston luku
        if uploaded_file.name.endswith('.xlsx'):
            df = pd.read_excel(uploaded_file)
        else:
            df = pd.read_csv(uploaded_file)
            
        st.success(f"Data ladattu! Rivimäärä: {len(df)}")

        # --- 1. TORJUNTAPROSENTIT ---
        st.header("🛡️ Ulkopelin torjuntatehokkuus")
        
        if 'pesat_teksti' in df.columns and 'tulos_teksti' in df.columns:
            df_clean = df[df['pesat_teksti'].notna()].copy()
            
            summary = df_clean.groupby('pesat_teksti').agg(
                Yritykset=('tulos_teksti', 'count'),
                Palot=('tulos_teksti', lambda x: x.astype(str).str.contains('Palo', case=False).sum())
            ).reset_index()
            
            summary['Torjunta%'] = (summary['Palot'] / summary['Yritykset'] * 100).round(1)
            
            jarjestys = {"0-1": 1, "1-2": 2, "2-3": 3, "3-Koti": 4}
            summary['sort'] = summary['pesat_teksti'].map(jarjestys)
            summary = summary.sort_values('sort').drop('sort', axis=1).fillna(0)
            
            st.table(summary)

        # --- 2. LUKKARI-INDEKSI (UUSI) ---
        st.header("🧙‍♂️ Lukkari-indeksi & Erikoistilanteet")
        
        # Etsitään tapahtumatekstistä avainsanoja
        # Esim: "Väärä", "Tolppa", "Irtoaminen", "Laiton"
        if 'tapahtuma_teksti' in df.columns:
            lukkari_keywords = ['Väärä', 'Laiton', 'Irtoaminen', 'Kärpänen']
            
            lukkari_events = df[df['tapahtuma_teksti'].astype(str).str.contains('|'.join(lukkari_keywords), case=False, na=False)]
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Lukkaritapahtumat", len(lukkari_events))
            with col2:
                vapaat = df[df['tapahtuma_teksti'].astype(str).str.contains('Vapaa', case=False, na=False)]
                st.metric("Vapaataipaleet", len(vapaat))
            with col3:
                viimeinen_laiton = df[df['tapahtuma_teksti'].astype(str).str.contains('viimeinen laiton', case=False, na=False)]
                st.metric("Viimeinen laiton", len(viimeinen_laiton))
            
            if not lukkari_events.empty:
                st.write("### Tarkat lukkari/erikoistapahtumat:")
                st.dataframe(lukkari_events[['vuoro_teksti', 'lyoja_nimi', 'tapahtuma_teksti', 'tulos_teksti']])

        # --- 3. LYÖNTISUUNTA JA TULOS ---
        st.header("🎯 Lyöntianalyysi")
        if 'lyonni_suunta' in df.columns:
            # Ristiintaulukointi: Suunta vs Tulos
            ct = pd.crosstab(df['lyonni_suunta'], df['tulos_teksti'])
            st.bar_chart(ct)

        # --- 4. PELAAJA-HAKU ---
        st.header("🔍 Etsi pelaajan suoritukset")
        pelaaja = st.selectbox("Valitse pelaaja:", options=sorted(df['lyoja_nimi'].unique()))
        pelaaja_df = df[df['lyoja_nimi'] == pelaaja]
        st.dataframe(pelaaja_df)

    except Exception as e:
        st.error(f"Virhe analyysissa: {e}")
else:
    st.info("Pudota yläpuolelle laajennettu Excel-tiedosto aloittaaksesi.")
