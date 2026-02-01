import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

# --- TEMA & UI (KEKAL BEIGE & RED) ---
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
    .stButton>button { background-color: #b11e23 !important; color: white !important; width: 100%; border-radius: 0px; font-weight: bold; height: 50px; border: none; }
    section[data-testid="stSidebar"] { background-color: #2b2b2b !important; }
    section[data-testid="stSidebar"] * { color: #ffffff !important; }
    </style>
    """, unsafe_allow_html=True)

# --- SAMBUNGAN GOOGLE SHEETS ---
# Pastikan URL Sheets kau diletakkan di Streamlit Secrets (gsheets_url)
# Atau letak sementara kat sini untuk test:
URL_SHEET = "https://docs.google.com/spreadsheets/d/14jm7YfVyw3pACKMAstFc9X23pmEafugIxTE_Kcra8ck/edit?usp=sharing"

conn = st.connection("gsheets", type=GSheetsConnection)

def load_gsheet(worksheet_name):
    try:
        return conn.read(spreadsheet=URL_SHEET, worksheet=worksheet_name)
    except:
        return pd.DataFrame()

# --- SIDEBAR ---
st.sidebar.markdown("<h1 style='text-align: center; color: #b11e23;'>GARISBAWAH ⭐</h1>", unsafe_allow_html=True)
menu = st.sidebar.radio("NAVIGASI", ["📈 DASHBOARD", "💰 UPDATE SALES", "🛒 UPDATE STOK", "📁 TUTUP AKAUN"])

# --- 1. DASHBOARD ---
if menu == "📈 DASHBOARD":
    st.title("BUSINESS DASHBOARD")
    df_jual = load_gsheet("Sales")
    df_stok = load_gsheet("Stok")
    
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

    if not df_jual.empty:
        st.write("### Trend Jualan Harian")
        df_plot = df_jual.copy()
        df_plot['Tarikh'] = pd.to_datetime(df_plot['Tarikh'], dayfirst=True, errors='coerce')
        df_plot = df_plot.dropna(subset=['Tarikh']).sort_values('Tarikh')
        
        fig = px.line(df_plot, x='Tarikh', y='Sales', markers=True)
        fig.update_traces(line_color='#b11e23', line_width=3, marker=dict(size=8))
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', hovermode="x unified")
        st.plotly_chart(fig, use_container_width=True)

# --- 2. UPDATE SALES ---
elif menu == "💰 UPDATE SALES":
    st.title("REKOD JUALAN")
    df_jual = load_gsheet("Sales")
    
    with st.form("form_sales", clear_on_submit=True):
        tgl = st.date_input("Tarikh", datetime.now())
        s = st.number_input("Sales (RM)", min_value=0.0, step=0.01, format="%.2f")
        p = st.number_input("Profit (RM)", min_value=0.0, step=0.01, format="%.2f")
        submit = st.form_submit_button("SIMPAN SALES KE CLOUD")
        
        if submit:
            kos_kira = float(s) - float(p)
            new_row = pd.DataFrame([{
                'Tarikh': tgl.strftime("%d-%m-%Y"),
                'Sales': float(s),
                'Profit': float(p),
                'Kos': float(kos_kira)
            }])
            updated_df = pd.concat([df_jual, new_row], ignore_index=True)
            conn.update(spreadsheet=URL_SHEET, worksheet="Sales", data=updated_df)
            st.success("✅ Data tersimpan di Google Sheets!")
            st.rerun()

# --- 3. UPDATE STOK ---
elif menu == "🛒 UPDATE STOK":
    st.title("BELANJA STOK")
    df_stok = load_gsheet("Stok")
    
    with st.form("form_stok", clear_on_submit=True):
        tgl = st.date_input("Tarikh", datetime.now())
        user = st.selectbox("Siapa Update?", ["Pijoy", "Amir", "Afiq"])
        item = st.text_input("Beli Apa?")
        harga = st.number_input("Harga (RM)", min_value=0.0, step=0.1)
        submit = st.form_submit_button("REKOD BELANJA KE CLOUD")
        
        if submit:
            new_row = pd.DataFrame([{
                'Tarikh': tgl.strftime("%d-%m-%Y"),
                'User': user,
                'Item': item,
                'Harga': harga
            }])
            updated_df = pd.concat([df_stok, new_row], ignore_index=True)
            conn.update(spreadsheet=URL_SHEET, worksheet="Stok", data=updated_df)
            st.success("✅ Stok dikemas kini!")
            st.rerun()

    st.markdown("---")
    st.subheader("📋 Rekod Perbelanjaan Terkini")
    if not df_stok.empty:
        st.dataframe(df_stok.iloc[::-1], use_container_width=True)
    else:
        st.info("Belum ada rekod di Google Sheets.")

# --- 4. TUTUP AKAUN ---
elif menu == "📁 TUTUP AKAUN":
    st.title("PENUTUP AKAUN")
    d_mula = st.date_input("Mula")
    d_akhir = st.date_input("Tamat")
    
    if st.button("JANA LAPORAN"):
        df = load_gsheet("Sales")
        if not df.empty:
            df['Tarikh_DT'] = pd.to_datetime(df['Tarikh'], format="%d-%m-%Y", errors='coerce')
            mask = (df['Tarikh_DT'] >= pd.Timestamp(d_mula)) & (df['Tarikh_DT'] <= pd.Timestamp(d_akhir))
            report = df.loc[mask]
            st.dataframe(report[['Tarikh', 'Sales', 'Profit', 'Kos']], use_container_width=True)

            st.metric("Total Profit Tempoh Ini", f"RM {report['Profit'].sum():.2f}")
