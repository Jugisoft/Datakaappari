import streamlit as st
import pandas as pd

st.set_page_config(page_title="Pesis PRO-Analysaattori", layout="wide")

st.title("⚾ Pesis-Analysaattori: Power Query Import")

# Ohjeistus
st.info("Pudota alle Power Queryllä tallentamasi 'events_.csv' tiedosto.")

uploaded_file = st.file_uploader("Valitse otteludata (CSV)", type=['csv'])

if uploaded_file:
    # Luetaan data (huomioidaan Power Queryn mahdolliset erikoisuudet)
    df = pd.read_csv(uploaded_file)
    
    st.success(f"Analysoidaan ottelua. Tapahtumia yhteensä: {len(df)}")

    # --- 1. TORJUNTAPROSENTIT (Vedonlyöntiyhtiön standardi) ---
    st.header("🛡️ Ulkopelin torjuntatilastot")
    
    # Suodatetaan vain ne rivit, joissa on yritys pesävälillä
    # Katsotaan 'pesat_teksti' ja 'tulos_teksti'
    if 'pesat_teksti' in df.columns and 'tulos_teksti' in df.columns:
        # Lasketaan yritykset ja palot per väli
        summary = df.groupby('pesat_teksti').agg(
            Yritykset=('tulos_teksti', 'count'),
            Torjunnat=('tulos_teksti', lambda x: (x.str.contains('Palo', na=False)).sum())
        ).reset_index()
        
        # Lasketaan prosentit
        summary['Torjunta%'] = (summary['Torjunnat'] / summary['Yritykset'] * 100).round(1)
        
        # Järjestetään loogisesti: 0-1, 1-2, 2-3, 3-Koti
        vali_jarjestys = {"0-1": 1, "1-2": 2, "2-3": 3, "3-Koti": 4}
        summary['order'] = summary['pesat_teksti'].map(vali_jarjestys)
        summary = summary.sort_values('order').drop('order', axis=1)
        
        st.table(summary)
        

    # --- 2. LUKKARIN JA ULKOPELAAJIEN ERIKOISET ---
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("👤 Ulkopelaajien palot")
        # Jos datassa on ulkopelaaja-sarake (tapahtuma_teksti sisältää usein nimen)
        st.write("Yleisimmät tapahtumat:")
        st.write(df['tapahtuma_teksti'].value_counts().head(10))

    with col2:
        st.subheader("🎯 Lyöntisuunnat")
        if 'lyonni_suunta' in df.columns:
            st.bar_chart(df['lyonni_suunta'].value_counts())

    # --- 3. RAAKADATA EXPORT ---
    st.divider()
    with st.expander("Selaa ja lataa puhdistettu data"):
        st.dataframe(df)
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("Lataa puhdistettu CSV", csv, "puhdistettu_data.csv", "text/csv")
