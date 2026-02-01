import csv
from datetime import datetime
import os

FILE_JUALAN = 'garisbawah.csv'
FILE_STOK = 'stock.csv'

def prepare_files():
    # Header baru dengan Profit & Kos untuk Jualan, dan User untuk Stok
    if not os.path.exists(FILE_JUALAN):
        with open(FILE_JUALAN, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Tarikh', 'Sales', 'Profit', 'Kos'])
    if not os.path.exists(FILE_STOK):
        with open(FILE_STOK, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Tarikh', 'User', 'Item', 'Harga'])

def sort_csv_by_date(filename):
    """Fungsi Mechatronic: Memastikan data dalam CSV sentiasa tersusun ikut masa."""
    data = []
    with open(filename, 'r') as f:
        reader = csv.DictReader(f)
        header = reader.fieldnames
        for row in reader:
            data.append(row)
    
    # Susun ikut objek datetime
    try:
        data.sort(key=lambda x: datetime.strptime(x['Tarikh'], "%d-%m-%Y"))
        with open(filename, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=header)
            writer.writeheader()
            writer.writerows(data)
    except:
        pass # Skip kalau ada tarikh rosak

# --- OPTION 1: UPDATE SALES ---
def update_sales():
    prepare_files()
    print("\n--- [1] UPDATE SALES HARIAN ---")
    tarikh = input("Tarikh (DD-MM-YYYY) [Enter untuk hari ini]: ") or datetime.now().strftime("%d-%m-%Y")
    try:
        sales = float(input("Sales Harian (RM): "))
        profit = float(input("Profit Harian (RM): "))
        kos = sales - profit 
        
        with open(FILE_JUALAN, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([tarikh, sales, profit, kos])
        
        sort_csv_by_date(FILE_JUALAN) # Biar fail tersusun
        print(f"✅ Berjaya! Sales: RM{sales:.2f}, Profit: RM{profit:.2f}")
    except ValueError:
        print("❌ Error: Masukkan nombor sahaja!")

# --- OPTION 2: UPDATE KOS (BELI STOK) ---
def update_kos():
    prepare_files()
    print("\n--- [2] UPDATE KOS (BELI STOK) ---")
    tarikh = input("Tarikh (DD-MM-YYYY) [Enter untuk hari ini]: ") or datetime.now().strftime("%d-%m-%Y")
    
    # TAMBAH USER: Supaya tahu siapa shopping
    user = input("Nama Owner (Payer): ") or "Unknown"
    item = input("Beli apa? (e.g. Susu): ")
    
    try:
        harga = float(input("Berapa Ringgit (RM): "))
        with open(FILE_STOK, 'a', newline='') as f:
            writer = csv.writer(f)
            # Masukkan User dalam rekod
            writer.writerow([tarikh, user, item, harga])
        
        sort_csv_by_date(FILE_STOK)
        print(f"✅ Rekod {item} oleh {user} berjaya disimpan.")
    except ValueError:
        print("❌ Error: Masukkan nombor sahaja!")

# --- OPTION 3: CURRENT CHECK ---
def current_check():
    t_sales, t_profit, t_kos_jualan, t_belanja_stok = 0.0, 0.0, 0.0, 0.0

    if os.path.exists(FILE_JUALAN):
        with open(FILE_JUALAN, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    t_sales += float(row['Sales'])
                    t_profit += float(row['Profit'])
                    t_kos_jualan += float(row['Kos'])
                except: continue

    if os.path.exists(FILE_STOK):
        with open(FILE_STOK, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    t_belanja_stok += float(row['Harga'])
                except: continue

    current_kos = t_kos_jualan - t_belanja_stok

    print("\n===== [3] CURRENT CHECK =====")
    print(f"Total Sales  : RM {t_sales:.2f}")
    print(f"Total Profit : RM {t_profit:.2f}")
    print(f"Baki Modal   : RM {current_kos:.2f} (Duit baki jualan - belanja stok)")
    print("==============================")

# --- OPTION 4: TUTUP ACCOUNT ---
def tutup_account():
    print("\n--- [4] TUTUP ACCOUNT (TARIKH SPECIFIC) ---")
    start_str = input("Tarikh Mula (DD-MM-YYYY): ").strip()
    end_str = input("Tarikh Akhir (DD-MM-YYYY): ").strip()
    
    try:
        start_d = datetime.strptime(start_str, "%d-%m-%Y")
        end_d = datetime.strptime(end_str, "%d-%m-%Y")
        
        s_sales, s_profit, s_kos = 0.0, 0.0, 0.0
        found = False
        
        if os.path.exists(FILE_JUALAN):
            with open(FILE_JUALAN, 'r') as f:
                reader = csv.DictReader(f)
                print(f"\nREKOD DALAM RANGE {start_str} -> {end_str}:")
                print("-" * 50)
                for row in reader:
                    try:
                        date_str = row['Tarikh'].strip()
                        d_file = datetime.strptime(date_str, "%d-%m-%Y")
                        
                        if start_d <= d_file <= end_d:
                            print(f"{date_str} | Sales: RM{row['Sales']} | Profit: RM{row['Profit']}")
                            s_sales += float(row['Sales'])
                            s_profit += float(row['Profit'])
                            s_kos += float(row['Kos'])
                            found = True
                    except: continue
            
            if found:
                print("-" * 50)
                print(f"TOTAL SALES  : RM {s_sales:.2f}")
                print(f"TOTAL PROFIT : RM {s_profit:.2f}")
                print("-" * 50)
            else:
                print("ℹ️ Tiada rekod dijumpai.")
    except ValueError:
        print("❌ Format tarikh salah!")

# --- MAIN MENU ---
while True:
    print("\n[ GARISBAWAH COFFEE SYSTEM - CLI ]")
    print("1. Update Sales")
    print("2. Update Kos (Beli Stok)")
    print("3. Current Check")
    print("4. Tutup Account")
    print("5. Close")
    
    p = input("Pilihan anda: ")
    if p == '1': update_sales()
    elif p == '2': update_kos()
    elif p == '3': current_check()
    elif p == '4': tutup_account()
    elif p == '5': 
        print("Jumpa lagi! ☕")
        break
    else:
        print("Pilihan salah!")