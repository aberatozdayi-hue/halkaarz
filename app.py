import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Halka Arz Pro Takip", layout="wide")

st.title("📈 Halka Arz Portföy Terminali")

# Portföy Verilerin (SVGYO 169 Lot, GENKM 155 Lot güncel)
if 'df' not in st.session_state:
    data = {
        "Hisse": ["GENKM", "SVGYO", "LXGYO", "MCARD"],
        "Alış Fiyatı": [11.00, 3.25, 12.05, 80.00],
        "Lot": [155, 169, 55, 9], 
        "Güncel Fiyat": [13.31, 4.50, 12.05, 80.00]
    }
    st.session_state.df = pd.DataFrame(data)

# Yan Panel: Veri Düzenleme
st.sidebar.header("📝 Portföy Yönetimi")
secilen_hisse = st.sidebar.selectbox("Hisse Seç veya Yaz", st.session_state.df["Hisse"].tolist())

yeni_alis = st.sidebar.number_input("Alış Fiyatı", value=float(st.session_state.df.loc[st.session_state.df['Hisse'] == secilen_hisse, 'Alış Fiyatı'].iloc[0]), step=0.01)
yeni_lot = st.sidebar.number_input("Lot Sayısı", value=int(st.session_state.df.loc[st.session_state.df['Hisse'] == secilen_hisse, 'Lot'].iloc[0]), step=1)
yeni_guncel = st.sidebar.number_input("Güncel Borsa Fiyatı", value=float(st.session_state.df.loc[st.session_state.df['Hisse'] == secilen_hisse, 'Güncel Fiyat'].iloc[0]), step=0.01)

if st.sidebar.button("Rakamları Kaydet ve Güncelle"):
    st.session_state.df.loc[st.session_state.df['Hisse'] == secilen_hisse, 'Alış Fiyatı'] = yeni_alis
    st.session_state.df.loc[st.session_state.df['Hisse'] == secilen_hisse, 'Lot'] = yeni_lot
    st.session_state.df.loc[st.session_state.df['Hisse'] == secilen_hisse, 'Güncel Fiyat'] = yeni_guncel
    st.success(f"{secilen_hisse} başarıyla güncellendi!")

# Hesaplamalar
df = st.session_state.df.copy()
df["Maliyet"] = df["Alış Fiyatı"] * df["Lot"]
df["Değer"] = df["Güncel Fiyat"] * df["Lot"]
df["Kar (TL)"] = df["Değer"] - df["Maliyet"]
df["Kar %"] = (df["Kar (TL)"] / df["Maliyet"]) * 100

# Üst Özet Kartları
c1, c2, c3, c4 = st.columns(4)
toplam_maliyet = df['Maliyet'].sum()
toplam_deger = df['Değer'].sum()
toplam_kar = toplam_deger - toplam_maliyet

c1.metric("Toplam Yatırım", f"{toplam_maliyet:,.2f} TL")
c2.metric("Portföy Değeri", f"{toplam_deger:,.2f} TL")
c3.metric("Toplam Kar", f"{toplam_kar:,.2f} TL", f"%{(toplam_kar/toplam_maliyet)*100:.2f}")
c4.metric("Hisse Adedi", len(df))

st.divider()

# Grafikler ve Tablo Yan Yana
col_tablo, col_grafik = st.columns([2, 1])

with col_tablo:
    st.subheader("📊 Hisse Bazlı Performans")
    st.dataframe(df.style.format({
        "Alış Fiyatı": "{:.2f} TL", "Güncel Fiyat": "{:.2f} TL", 
        "Maliyet": "{:.2f} TL", "Değer": "{:.2f} TL", 
        "Kar (TL)": "{:.2f} TL", "Kar %": "%{:.2f}"
    }), use_container_width=True)

with col_grafik:
    st.subheader("🍕 Portföy Dağılımı")
    fig = px.pie(df, values='Değer', names='Hisse', hole=0.4, color_discrete_sequence=px.colors.qualitative.Pastel)
    st.plotly_chart(fig, use_container_width=True)

st.divider()

# Tavan Serisi Tahmincisi (LXGYO ve GENKM için özel)
st.subheader("🚀 Tavan Serisi Kar Tahmincisi")
st.info("Bu bölüm, seçtiğiniz hissenin üst üste tavan yapması durumunda oluşacak karı hesaplar.")

t_hisse = st.selectbox("Tahmin Yapılacak Hisse", df["Hisse"])
t_gun = st.slider("Kaç Gün Tavan Gider?", 1, 10, 5)

t_lot = df.loc[df['Hisse'] == t_hisse, 'Lot'].iloc[0]
t_baslangic = df.loc[df['Hisse'] == t_hisse, 'Güncel Fiyat'].iloc[0]
t_maliyet = df.loc[df['Hisse'] == t_hisse, 'Maliyet'].iloc[0]

t_fiyatlar = []
current_price = t_baslangic
for i in range(t_gun):
    current_price = current_price * 1.10
    t_fiyatlar.append(round(current_price, 2))

t_son_deger = t_fiyatlar[-1] * t_lot
t_kar = t_son_deger - t_maliyet

st.write(f"**{t_gun}** gün sonra tahmin edilen fiyat: **{t_fiyatlar[-1]} TL**")
st.write(f"Tahmin edilen toplam kar: **{t_kar:,.2f} TL**")
