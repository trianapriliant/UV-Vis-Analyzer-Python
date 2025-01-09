import os
import pandas as pd
import matplotlib.pyplot as plt

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

# Data untuk grafik dan perhitungan degradasi
all_lambda = []
all_absorbansi = []

# Proses setiap file CSV
for file_path in file_paths:
    # Baca file mulai dari baris ke-46 (skip header)
    df = pd.read_csv(file_path, skiprows=45, delimiter="\t", header=None)
    
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
    
    # Menambahkan data ke dalam list untuk plot dan analisis degradasi
    all_lambda.append(df['Lambda'])
    all_absorbansi.append(df['Absorbansi'])

# Gabungkan data
result = data_frames[0][['Nomor', 'Lambda']].copy()  # Ambil kolom Nomor dan Lambda dari file pertama
for i, df in enumerate(data_frames):
    result[f"Abs Sampel {i+1}"] = df['Absorbansi']

# Simpan ke file CSV di folder hasil
output_file = os.path.join(output_folder, "AbsSampel.csv")
result.to_csv(output_file, index=False)
print(f"File berhasil disimpan sebagai {output_file}")

# Menghitung nilai absorbansi tertinggi untuk setiap sampel dan degradasi bertahap
abs_max_values = []
for i, df in enumerate(data_frames):
    abs_max = df['Absorbansi'].max()
    abs_max_values.append(abs_max)

# Menghitung persentase degradasi bertahap dari sampel pertama ke sampel lainnya
degradasi_values = []
abs_max_sampel_pertama = abs_max_values[0]
for i in range(1, len(abs_max_values)):
    abs_max_sampel_selanjutnya = abs_max_values[i]
    if abs_max_sampel_pertama != 0:
        degradasi = ((abs_max_sampel_pertama - abs_max_sampel_selanjutnya) / abs_max_sampel_pertama) * 100
        degradasi_values.append(degradasi)
    else:
        degradasi_values.append(0)

# Menampilkan hasil degradasi bertahap
for i, degradasi in enumerate(degradasi_values, 1):
    print(f"Persentase degradasi dari Sampel 1 ke Sampel {i+1}: {degradasi:.2f}%")

# Plot grafik hubungan Lambda dan Absorbansi untuk seluruh sampel
plt.figure(figsize=(10, 6))
for i, df in enumerate(data_frames):
    # Plot absorbansi dengan label
    plt.plot(df['Lambda'], df['Absorbansi'], label=f'Sampel {i+1}')
    
    # Cari titik absorbansi tertinggi dan beri tanda
    abs_max_idx = df['Absorbansi'].idxmax()  # Indeks dari nilai absorbansi tertinggi
    max_lambda = df['Lambda'].iloc[abs_max_idx]
    max_abs = df['Absorbansi'].iloc[abs_max_idx]
    
    # Tandai titik dengan marker dan tampilkan nilai absorbansi
    plt.scatter(max_lambda, max_abs, color='red', zorder=5)
    plt.text(max_lambda, max_abs, f'{max_abs:.2f}', color='black', fontsize=9, ha='left', va='bottom')

# Tambahkan persentase degradasi pada gambar di pojok kiri atas
degradasi_text = '\n'.join([f'Degradasi Sampel 1 ke {i+1}: {degradasi_values[i-1]:.2f}%' for i in range(1, len(degradasi_values)+1)])
plt.text(0.05, 0.95, degradasi_text, transform=plt.gca().transAxes,
         fontsize=9, color='black', ha='left', va='top', bbox=dict(facecolor='white', edgecolor='black', boxstyle='round,pad=0.25'))

# Label dan judul
plt.xlabel('Lambda (nm)')
plt.ylabel('Absorbansi')
plt.title('Hubungan Lambda dengan Absorbansi untuk Setiap Sampel')
plt.legend()
plt.grid(True)
plt.tight_layout()

# Simpan grafik ke file
plt.savefig(os.path.join(output_folder, 'grafik_lamda_absorbansi.png'))

# Tampilkan grafik
plt.show()
