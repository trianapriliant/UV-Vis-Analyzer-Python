import os
import pandas as pd

# Path folder tempat file CSV berada
folder_path = "./csv"  # Ganti dengan path folder tempat file CSV Anda

# Folder untuk menyimpan output
output_folder = "./GabunganAbsSampel"
os.makedirs(output_folder, exist_ok=True)  # Membuat folder hasil jika belum ada

# Ambil semua file CSV di folder
file_paths = [os.path.join(folder_path, file) for file in os.listdir(folder_path) if file.endswith('.csv')]

# Periksa apakah ada file CSV
if not file_paths:
    print("Tidak ada file CSV ditemukan di folder:", folder_path)
    exit()

# Inisialisasi list untuk menyimpan DataFrame
data_frames = []

# Proses setiap file CSV
for file_path in file_paths:
    # Baca file mulai dari baris ke-46 (skip header)
    df = pd.read_csv(file_path, skiprows=45, delimiter="\t", header=None)
    
    # Debugging: Periksa isi file dan jumlah kolom
    print(f"Memproses file: {file_path}")
    print(f"Jumlah kolom: {df.shape[1]}")
    print(df.head())
    
    # Ambil hanya 3 kolom pertama jika file memiliki lebih dari 3 kolom
    if df.shape[1] >= 3:
        df = df.iloc[:, :3]  # Ambil kolom pertama hingga ketiga
    else:
        raise ValueError(f"File {file_path} memiliki kurang dari 3 kolom!")

    # Batasi data hanya sampai baris ke-800 (jika ada lebih dari 800 baris)
    df = df.head(800)
    
    # Beri nama kolom
    df.columns = ['Nomor', 'Lambda', 'Absorbansi']
    
    # Konversi tipe data ke numeric (jika perlu)
    df['Nomor'] = pd.to_numeric(df['Nomor'], errors='coerce')
    df['Lambda'] = pd.to_numeric(df['Lambda'], errors='coerce')
    df['Absorbansi'] = pd.to_numeric(df['Absorbansi'], errors='coerce')
    
    data_frames.append(df)

# Gabungkan data
result = data_frames[0][['Nomor', 'Lambda']].copy()  # Ambil kolom Nomor dan Lambda dari file pertama
for i, df in enumerate(data_frames):
    result[f"Abs Sampel {i+1}"] = df['Absorbansi']

# Simpan ke file CSV di folder hasil
output_file = os.path.join(output_folder, "AbsSampel.csv")
result.to_csv(output_file, index=False)
print(f"File berhasil disimpan sebagai {output_file}")
