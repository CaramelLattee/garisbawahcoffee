import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import os

# --- KONFIGURASI FAIL ---
FILE_JUALAN = 'garisbawah.csv'
FILE_STOK = 'stock.csv'

# --- TEMA & UI (BEIGE & RED) ---
st.set_page_config(page_title="Garisbawah Coffee", page_icon="☕", layout="centered")

st.markdown("""
    <style>
    .stApp { background-color: #f5f5dc; }
    h1, h2, h3 { color: #b11e23 !important; font-family: 'Impact', sans-serif; letter-spacing: 1px; }
    p, label, .stMarkdown { color: #2b2b2b !important; font-weight: 600; }
    div[data-testid="stMetricValue"] { color: #b11e23 !important; font-size: 35px; font-weight: bold; }
    div[data-testid="stMetric"] { 
        background-color: #ffffff; 
        padding: 20px; border-radius: 5px; border: 2px solid #b11e23; box-shadow: 4px 4px 0px #b11e23;
    }
    .stButton>button { background-color: #b11e23; color: white; width: 100%; border-radius: 0px; font-weight: bold; height: 50px; border: none; }
    .stButton>button:hover { background-color: #ffffff; color: #b11e23; border: 2px solid #b11e23; }
    section[data-testid="stSidebar"] { background-color: #2b2b2b !important; }
    section[data-testid="stSidebar"] * { color: #ffffff !important; }
    </style>
    """, unsafe_allow_html=True)

# --- FUNGSI DATA ---
def load_data(file):
    if os.path.exists(file):
        return pd.read_csv(file)
    return pd.DataFrame()

# --- SIDEBAR ---
st.sidebar.markdown("<h1 style='text-align: center; color: #b11e23;'>GARISBAWAH ⭐</h1>", unsafe_allow_html=True)
menu = st.sidebar.radio("NAVIGASI", ["📈 DASHBOARD", "💰 UPDATE SALES", "🛒 UPDATE STOK", "📁 TUTUP AKAUN"])

# --- 1. DASHBOARD ---
if menu == "📈 DASHBOARD":
    st.title("BUSINESS DASHBOARD")
    df_jual = load_data(FILE_JUALAN)
    df_stok = load_data(FILE_STOK)
    
    # Kiraan Metric
    total_sales = df_jual['Sales'].sum() if not df_jual.empty else 0
    total_profit = df_jual['Profit'].sum() if not df_jual.empty else 0
    total_kos_jualan = df_jual['Kos'].sum() if not df_jual.empty else 0
    total_belanja_stok = df_stok['Harga'].sum() if not df_stok.empty else 0
    baki_modal = total_kos_jualan - total_belanja_stok

    col1, col2, col3 = st.columns(3)
    col1.metric("TOTAL SALES", f"RM {total_sales:.2f}")
    col2.metric("TOTAL PROFIT", f"RM {total_profit:.2f}")
    col3.metric("BAKI MODAL", f"RM {baki_modal:.2f}")

    st.markdown("---")

    # Graf Plotly Merah
    if not df_jual.empty:
        st.write("### Trend Jualan Harian")
        df_plot = df_jual.copy()
        df_plot['Tarikh'] = pd.to_datetime(df_plot['Tarikh'], dayfirst=True, errors='coerce')
        df_plot = df_plot.dropna(subset=['Tarikh']).sort_values('Tarikh')
        
        fig = px.line(df_plot, x='Tarikh', y='Sales', markers=True)
        fig.update_traces(line_color='#b11e23', line_width=3, marker=dict(size=8))
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', hovermode="x unified")
        st.plotly_chart(fig, use_container_width=True)

# --- 2. UPDATE SALES (VERSI RE-SYNC) ---
elif menu == "💰 UPDATE SALES":
    st.title("REKOD JUALAN")
    with st.form("form_sales", clear_on_submit=True): # clear_on_submit supaya form kosong balik lepas tekan
        tgl = st.date_input("Tarikh", datetime.now())
        s = st.number_input("Sales (RM)", min_value=0.0, step=0.01, format="%.2f")
        p = st.number_input("Profit (RM)", min_value=0.0, step=0.01, format="%.2f")
        submit = st.form_submit_button("SIMPAN SALES")
        
        if submit:
            # 1. Kira kos secara manual
            kos_kira = float(s) - float(p)
            
            # 2. Susun data dalam bentuk dictionary yang SANGAT JELAS
            data_baru = {
                'Tarikh': tgl.strftime("%d-%m-%Y"),
                'Sales': float(s),
                'Profit': float(p),
                'Kos': float(kos_kira)
            }
            
            # 3. Tukar ke DataFrame
            df_baru = pd.DataFrame([data_baru])
            
            # 4. Simpan ke CSV (Guna cara append yang paling selamat)
            if not os.path.isfile(FILE_JUALAN):
                df_baru.to_csv(FILE_JUALAN, index=False)
            else:
                df_baru.to_csv(FILE_JUALAN, mode='a', header=False, index=False)
            
            st.success(f"✅ DATA MASUK: Sales RM{s:.2f} | Profit RM{p:.2f}")
            st.balloons() # Saja bagi gempak sikit bila berjaya
            st.rerun()

# --- 3. UPDATE STOK (ADA PREVIEW DATA) ---
elif menu == "🛒 UPDATE STOK":
    st.title("BELANJA STOK")
    
    # Bahagian Input
    with st.form("form_stok", clear_on_submit=True):
        tgl = st.date_input("Tarikh", datetime.now())
        user = st.selectbox("Siapa Update?", ["Pijoy", "Amir", "Afiq"])
        item = st.text_input("Beli Apa? (Contoh: Susu/Biji Kopi)")
        harga = st.number_input("Harga (RM)", min_value=0.0, step=0.1)
        submit = st.form_submit_button("REKOD BELANJA")
        
        if submit:
            new_stok = pd.DataFrame([[tgl.strftime("%d-%m-%Y"), user, item, harga]], 
                                    columns=['Tarikh','User','Item','Harga'])
            new_stok.to_csv(FILE_STOK, mode='a', header=not os.path.exists(FILE_STOK), index=False)
            st.success(f"RM {harga:.2f} direkodkan oleh {user}")
            st.rerun() # Auto-refresh supaya jadual kat bawah terus update

    st.markdown("---")
    
    # BAHAGIAN BARU: TENGOK DATA LEPAS KEY-IN
    st.subheader("📋 Rekod Perbelanjaan Terkini")
    df_stok_view = load_data(FILE_STOK)
    
    if not df_stok_view.empty:
        # Kita terbalikkan urutan supaya yang paling baru masuk ada kat atas (LIFO)
        st.dataframe(df_stok_view.iloc[::-1], use_container_width=True)
        
        # Tambah fungsi kira total belanja stok sekejap
        total_stok = df_stok_view['Harga'].sum()
        st.info(f"Jumlah keseluruhan belanja stok: **RM {total_stok:.2f}**")
    else:
        st.write("Belum ada rekod stok.")

# --- 4. TUTUP AKAUN ---
elif menu == "📁 TUTUP AKAUN":
    st.title("PENUTUP AKAUN")
    d_mula = st.date_input("Mula")
    d_akhir = st.date_input("Tamat")
    
    if st.button("JANA LAPORAN"):
        df = load_data(FILE_JUALAN)
        if not df.empty:
            df['Tarikh_DT'] = pd.to_datetime(df['Tarikh'], format="%d-%m-%Y", errors='coerce')
            mask = (df['Tarikh_DT'] >= pd.Timestamp(d_mula)) & (df['Tarikh_DT'] <= pd.Timestamp(d_akhir))
            report = df.loc[mask]
            st.dataframe(report[['Tarikh', 'Sales', 'Profit', 'Kos']], use_container_width=True)
            st.metric("Total Profit Tempoh Ini", f"RM {report['Profit'].sum():.2f}")