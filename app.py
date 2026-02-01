import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

# --- KONFIGURASI UI ---
st.set_page_config(page_title="Garisbawah Coffee", page_icon="☕", layout="centered")

st.markdown("""
    <style>
    .stApp { background-color: #f5f5dc; }
    h1, h2, h3 { color: #b11e23 !important; font-family: 'Impact', sans-serif; }
    div[data-testid="stMetric"] { 
        background-color: #ffffff; padding: 20px; border-radius: 5px; 
        border: 2px solid #b11e23; box-shadow: 4px 4px 0px #b11e23;
    }
    .stButton>button { background-color: #b11e23 !important; color: white !important; font-weight: bold; }
    section[data-testid="stSidebar"] { background-color: #2b2b2b !important; }
    section[data-testid="stSidebar"] * { color: #ffffff !important; }
    </style>
    """, unsafe_allow_html=True)

# --- SAMBUNGAN GOOGLE SHEETS (DARI SECRETS) ---
try:
    # URL diambil terus dari Settings > Secrets (gsheets_url)
    URL_SHEET = st.secrets["gsheets_url"]
    conn = st.connection("gsheets", type=GSheetsConnection)
except Exception as e:
    st.error("Sila masukkan 'gsheets_url' dalam Streamlit Secrets!")
    st.stop()

def load_gsheet(worksheet_name):
    try:
        # ttl=0 supaya data sentiasa fresh setiap kali refresh
        return conn.read(spreadsheet=URL_SHEET, worksheet=worksheet_name, ttl=0)
    except:
        # Jika sheet kosong/tak wujud, bagi DataFrame kosong dengan header yang betul
        if worksheet_name == "Sales":
            return pd.DataFrame(columns=['Tarikh', 'Sales', 'Profit', 'Kos'])
        return pd.DataFrame(columns=['Tarikh', 'User', 'Item', 'Harga'])

# --- SIDEBAR ---
st.sidebar.markdown("<h1 style='text-align: center;'>GARISBAWAH ⭐</h1>", unsafe_allow_html=True)
menu = st.sidebar.radio("NAVIGASI", ["📈 DASHBOARD", "💰 UPDATE SALES", "🛒 UPDATE STOK", "📁 TUTUP AKAUN"])

# --- 1. DASHBOARD ---
if menu == "📈 DASHBOARD":
    st.title("BUSINESS DASHBOARD")
    df_jual = load_gsheet("Sales")
    df_stok = load_gsheet("Stok")
    
    # Tukar column ke numeric untuk elak error kira-kira
    for col in ['Sales', 'Profit', 'Kos']:
        if col in df_jual.columns: df_jual[col] = pd.to_numeric(df_jual[col], errors='coerce').fillna(0)
    if 'Harga' in df_stok.columns: df_stok['Harga'] = pd.to_numeric(df_stok['Harga'], errors='coerce').fillna(0)

    total_sales = df_jual['Sales'].sum() if not df_jual.empty else 0
    total_profit = df_jual['Profit'].sum() if not df_jual.empty else 0
    total_kos_jualan = df_jual['Kos'].sum() if not df_jual.empty else 0
    total_belanja_stok = df_stok['Harga'].sum() if not df_stok.empty else 0
    baki_modal = total_kos_jualan - total_belanja_stok

    c1, c2, c3 = st.columns(3)
    c1.metric("TOTAL SALES", f"RM {total_sales:.2f}")
    c2.metric("TOTAL PROFIT", f"RM {total_profit:.2f}")
    c3.metric("BAKI MODAL", f"RM {baki_modal:.2f}")

    if not df_jual.empty:
        st.write("### Trend Jualan Harian")
        df_jual['Tarikh'] = pd.to_datetime(df_jual['Tarikh'], dayfirst=True, errors='coerce')
        fig = px.line(df_jual.sort_values('Tarikh'), x='Tarikh', y='Sales', markers=True)
        fig.update_traces(line_color='#b11e23')
        st.plotly_chart(fig, use_container_width=True)

# --- 2. UPDATE SALES ---
elif menu == "💰 UPDATE SALES":
    st.title("REKOD JUALAN")
    df_jual = load_gsheet("Sales")
    
    with st.form("form_sales", clear_on_submit=True):
        tgl = st.date_input("Tarikh", datetime.now())
        s = st.number_input("Sales (RM)", min_value=0.0, format="%.2f")
        p = st.number_input("Profit (RM)", min_value=0.0, format="%.2f")
        submit = st.form_submit_button("SIMPAN SALES KE GOOGLE SHEETS")
        
        if submit:
            kos_kira = float(s) - float(p)
            new_row = pd.DataFrame([{
                'Tarikh': tgl.strftime("%d-%m-%Y"),
                'Sales': s, 'Profit': p, 'Kos': kos_kira
            }])
            updated_df = pd.concat([df_jual, new_row], ignore_index=True)
            conn.update(spreadsheet=URL_SHEET, worksheet="Sales", data=updated_df)
            st.success("✅ Berjaya simpan!")
            st.rerun()

# --- 3. UPDATE STOK ---
elif menu == "🛒 UPDATE STOK":
    st.title("BELANJA STOK")
    df_stok = load_gsheet("Stok")
    
    with st.form("form_stok", clear_on_submit=True):
        tgl = st.date_input("Tarikh", datetime.now())
        user = st.selectbox("Owner", ["Pijoy", "Amir", "Afiq"])
        item = st.text_input("Barang")
        harga = st.number_input("Harga (RM)", min_value=0.0)
        submit = st.form_submit_button("SIMPAN STOK KE GOOGLE SHEETS")
        
        if submit:
            new_row = pd.DataFrame([{
                'Tarikh': tgl.strftime("%d-%m-%Y"),
                'User': user, 'Item': item, 'Harga': harga
            }])
            updated_df = pd.concat([df_stok, new_row], ignore_index=True)
            conn.update(spreadsheet=URL_SHEET, worksheet="Stok", data=updated_df)
            st.success("✅ Stok dikemas kini!")
            st.rerun()

    st.markdown("---")
    if not df_stok.empty:
        st.dataframe(df_stok.iloc[::-1], use_container_width=True)

# --- 4. TUTUP AKAUN ---
elif menu == "📁 TUTUP AKAUN":
    st.title("LAPORAN JUALAN")
    d_mula = st.date_input("Mula")
    d_akhir = st.date_input("Tamat")
    if st.button("JANA"):
        df = load_gsheet("Sales")
        df['DT'] = pd.to_datetime(df['Tarikh'], format="%d-%m-%Y", errors='coerce')
        report = df[(df['DT'] >= pd.Timestamp(d_mula)) & (df['DT'] <= pd.Timestamp(d_akhir))]
        st.dataframe(report[['Tarikh', 'Sales', 'Profit', 'Kos']], use_container_width=True)
