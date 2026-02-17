import streamlit as st
import pandas as pd

st.set_page_config(page_title="Pesis PRO: Syväanalyysi", layout="wide")

st.title("⚾ Pesis-Analysaattori PRO (Deep Data)")

uploaded_file = st.file_uploader("Lataa laajennettu Excel", type=['csv', 'xlsx'])

if uploaded_file:
    try:
        # Luetaan data
        df = pd.read_excel(uploaded_file) if uploaded_file.name.endswith('.xlsx') else pd.read_csv(uploaded_file)
        
        # FIX: Etsitään sarakkeet, vaikka niiden nimet olisivat muuttuneet
        # Käytetään batter_player_id:tä jos lyoja_nimi puuttuu
        lyoja_col = 'batter_player_id' if 'batter_player_id' in df.columns else (df.columns[0])
        tulos_col = 'texts' if 'texts' in df.columns else None
        palo_col = 'out' if 'out' in df.columns else None

        st.success(f"Data ladattu! Rivimäärä: {len(df)}")

        # --- 1. TORJUNTAPROSENTIT (PERUSTUEN 'OUT'-SARAKKEESEEN) ---
        st.header("🛡️ Ulkopelin torjuntatehokkuus")
        
        if tulos_col and palo_col:
            # Lasketaan yritykset ja palot
            # Tiedostossasi 'out' on True/False
            summary = df.groupby(tulos_col).agg(
                Yritykset=(palo_col, 'count'),
                Palot=(palo_col, lambda x: (x == True).sum() if x.dtype == bool else (x == 'True').sum())
            ).reset_index()
            
            summary['Torjunta%'] = (summary['Palot'] / summary['Yritykset'] * 100).round(1)
            st.table(summary)

        # --- 2. LUKKARI-INDEKSI ---
        st.header("🧙‍♂️ Lukkari-indeksi (Erikoistilanteet)")
        if tulos_col:
            # Etsitään 'texts' sarakkeesta erikoistermejä
            erikois = df[df[tulos_col].astype(str).str.contains('väärä|laiton|vapaa|kärpänen', case=False, na=False)]
            
            col1, col2 = st.columns(2)
            col1.metric("Erikoistapahtumat", len(erikois))
            
            if not erikois.empty:
                st.write("Tarkat tapahtumat (texts-sarake):")
                st.dataframe(erikois[[lyoja_col, tulos_col]])

        # --- 3. RAAKADATA ---
        with st.expander("Katso kaikki sarakkeet ja data"):
            st.write("Löytyneet sarakkeet:", df.columns.tolist())
            st.dataframe(df)

    except Exception as e:
        st.error(f"Virhe analyysissa: {e}")
        st.info("Vinkki: Power Query saattaa nimetä sarakkeet eri tavalla jokaisella laajennuskerralla.")
