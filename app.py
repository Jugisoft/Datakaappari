import streamlit as st
import pandas as pd

st.set_page_config(page_title="Pesis Data-Hub PRO", layout="wide")

st.title("⚾ Pesis Data-Hub: Vedonlyönti-Export")

# --- TIEDOSTON LATAUS ---
st.subheader("📁 Lataa Excel tai CSV")
uploaded_file = st.file_uploader("Raahaa tähän UP-tilasto tai Syöttölomake", type=['csv', 'xlsx'])

if uploaded_file:
    # Luetaan data
    if uploaded_file.name.endswith('.csv'):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)
    
    st.success(f"Ladattu: {uploaded_file.name}")
    
    # --- AUTOMAATTINEN MAPPING ---
    # Etsitään sarakkeet jotka vastaavat yhtiön tarpeita
    # (Perustuen antamiisi tiedostoihin)
    
    if 'Tilanne' in df.columns and 'Onnistuminen' in df.columns:
        st.header("📊 Vedonlyöntiyhtiön Plug & Play -raportti")
        
        # Luodaan yhteenveto pesäväleittäin
        # Käytetään sarakkeita: Tilanne, Onnistuminen, Suorittava ulkopelaaja
        
        # Käännetään 'Onnistuminen' numeeriseksi jos se on tekstiä
        if df['Onnistuminen'].dtype == 'object':
            df['Sisäpeli_Onnistui'] = df['Onnistuminen'].str.contains('Onnistunut', case=False, na=False).astype(int)
        else:
            df['Sisäpeli_Onnistui'] = df['Onnistuminen']

        # Lasketaan torjunnat (1 - sisäpelin onnistuminen)
        df['Torjunta'] = 1 - df['Sisäpeli_Onnistui']
        
        # Ryhmittely tilanteen mukaan
        summary = df.groupby('Tilanne').agg(
            Yritykset=('Onnistuminen', 'count'),
            Torjunnat=('Torjunta', 'sum')
        ).reset_index()
        
        summary['Torjunta%'] = (summary['Torjunnat'] / summary['Yritykset'] * 100).round(1)
        
        # Näytetään visualisointi
        st.table(summary)
        
        # --- PELAAJA-ANALYYSI ---
        if 'Suorittava ulkopelaaja' in df.columns:
            st.subheader("🎯 Pelaajakohtaiset Torjunnat")
            pelaaja_stats = df.groupby('Suorittava ulkopelaaja').agg(
                Palot=('Torjunta', 'sum'),
                Kaikki_Tilanteet=('Torjunta', 'count')
            ).sort_values('Palot', ascending=False)
            st.bar_chart(pelaaja_stats['Palot'])
            
        # --- LATAUS YHTIÖLLE ---
        csv_export = summary.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Lataa valmis raportti kertoimenlaskentaan",
            data=csv_export,
            file_name=f"UP_Raportti_{uploaded_file.name}.csv",
            mime='text/csv',
        )
    else:
        st.warning("Tiedostosta ei löytynyt sarakkeita 'Tilanne' ja 'Onnistuminen'. Varmista että käytät 'Syöttölomake'-pohjaa.")
        st.write("Löytyneet sarakkeet:", df.columns.tolist())

else:
    st.info("Odotetaan tiedostoa. Voit ladata tähän esimerkiksi ottelun syöttölomakkeen CSV-muodossa.")
