import streamlit as st
import pandas as pd

st.set_page_config(page_title="Halka Arz Takip", layout="wide")

st.title("📈 Halka Arz Portföy Takip Uygulaması")

# Portföy Verilerin (SVGYO 169 Lot olarak güncellendi)
if 'df' not in st.session_state:
    data = {
        "Hisse": ["GENKM", "SVGYO", "LXGYO", "MCARD"],
        "Alış Fiyatı": [11.00, 3.25, 12.05, 80.00],
        "Lot": [155, 169, 55, 9], 
        "Güncel Fiyat": [13.31, 4.50, 12.05, 80.00]
    }
    st.session_state.df = pd.DataFrame(data)

# Yan Panel: Veri Düzenleme
st.sidebar.header("📝 Verileri Güncelle")
secilen_hisse = st.sidebar.selectbox("Hisse Seç", st.session_state.df["Hisse"])
yeni_alis = st.sidebar.number_input("Alış Fiyatı", value=float(st.session_state.df.loc[st.session_state.df['Hisse'] == secilen_hisse, 'Alış Fiyatı'].iloc[0]), step=0.01)
yeni_lot = st.sidebar.number_input("Lot Sayısı", value=int(st.session_state.df.loc[st.session_state.df['Hisse'] == secilen_hisse, 'Lot'].iloc[0]), step=1)
yeni_guncel = st.sidebar.number_input("Güncel Borsa Fiyatı", value=float(st.session_state.df.loc[st.session_state.df['Hisse'] == secilen_hisse, 'Güncel Fiyat'].iloc[0]), step=0.01)

if st.sidebar.button("Rakamları Kaydet"):
    st.session_state.df.loc[st.session_state.df['Hisse'] == secilen_hisse, 'Alış Fiyatı'] = yeni_alis
    st.session_state.df.loc[st.session_state.df['Hisse'] == secilen_hisse, 'Lot'] = yeni_lot
    st.session_state.df.loc[st.session_state.df['Hisse'] == secilen_hisse, 'Güncel Fiyat'] = yeni_guncel
    st.success(f"{secilen_hisse} güncellendi!")

# Hesaplamalar
df = st.session_state.df.copy()
df["Maliyet"] = df["Alış Fiyatı"] * df["Lot"]
df["Değer"] = df["Güncel Fiyat"] * df["Lot"]
df["Kar (TL)"] = df["Değer"] - df["Maliyet"]
df["Kar %"] = (df["Kar (TL)"] / df["Maliyet"]) * 100

# Özet Kartları
c1, c2, c3 = st.columns(3)
c1.metric("Toplam Yatırım", f"{df['Maliyet'].sum():,.2f} TL")
c2.metric("Toplam Kar", f"{df['Kar (TL)'].sum():,.2f} TL", f"%{((df['Değer'].sum()/df['Maliyet'].sum())-1)*100:.2f}")
c3.metric("Hisse Sayısı", len(df))

# Kar Tablosu
st.subheader("📊 Performans Tablosu")
st.dataframe(df.style.format({
    "Alış Fiyatı": "{:.2f} TL", "Güncel Fiyat": "{:.2f} TL", 
    "Maliyet": "{:.2f} TL", "Değer": "{:.2f} TL", 
    "Kar (TL)": "{:.2f} TL", "Kar %": "%{:.2f}"
}), use_container_width=True)
