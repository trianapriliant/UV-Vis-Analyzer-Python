import os
import pandas as pd
import matplotlib.pyplot as plt
from tkinter import Tk, Label, Entry, Button, filedialog, messagebox

def process_data(folder_path, sample_names):
    try:
        # Folder untuk menyimpan output
        output_folder = "./GabunganAbsSampel"
        os.makedirs(output_folder, exist_ok=True)

        # Ambil semua file CSV di folder
        file_paths = [os.path.join(folder_path, file) for file in os.listdir(folder_path) if file.endswith('.csv')]

        # Periksa apakah ada file CSV
        if not file_paths:
            messagebox.showerror("Error", "Tidak ada file CSV ditemukan di folder!")
            return

        # Pastikan jumlah nama sampel sesuai dengan jumlah file
        if len(sample_names) != len(file_paths):
            messagebox.showerror("Error", "Jumlah nama sampel tidak sesuai dengan jumlah file CSV!")
            return

        # Inisialisasi list untuk menyimpan DataFrame
        data_frames = []

        # Proses setiap file CSV
        for file_path in file_paths:
            # Baca file mulai dari baris ke-46 (skip header)
            df = pd.read_csv(file_path, skiprows=45, delimiter="\t", header=None)
            
            # Ambil hanya 3 kolom pertama jika file memiliki lebih dari 3 kolom
            if df.shape[1] >= 3:
                df = df.iloc[:, :3]
            else:
                raise ValueError(f"File {file_path} memiliki kurang dari 3 kolom!")

            # Batasi data hanya sampai baris ke-800
            df = df.head(800)
            
            # Beri nama kolom
            df.columns = ['Nomor', 'Lambda', 'Absorbansi']
            
            # Konversi tipe data ke numeric
            df['Nomor'] = pd.to_numeric(df['Nomor'], errors='coerce')
            df['Lambda'] = pd.to_numeric(df['Lambda'], errors='coerce')
            df['Absorbansi'] = pd.to_numeric(df['Absorbansi'], errors='coerce')
            
            data_frames.append(df)

        # Gabungkan data
        result = data_frames[0][['Nomor', 'Lambda']].copy()
        for i, df in enumerate(data_frames):
            result[f"Abs {sample_names[i]}"] = df['Absorbansi']

        # Simpan ke file CSV di folder hasil
        output_file = os.path.join(output_folder, "AbsSampel.csv")
        result.to_csv(output_file, index=False)
        messagebox.showinfo("Sukses", f"File berhasil disimpan sebagai {output_file}")

        # Plot grafik hubungan Lambda dan Absorbansi untuk seluruh sampel
        plt.figure(figsize=(10, 6))
        for i, df in enumerate(data_frames):
            plt.plot(df['Lambda'], df['Absorbansi'], label=f'{sample_names[i]}')

        # Label dan judul
        plt.xlabel('Lambda (nm)')
        plt.ylabel('Absorbansi')
        plt.title('Hubungan Lambda dengan Absorbansi')
        plt.legend()
        plt.grid(True)
        plt.tight_layout()

        # Simpan grafik ke file
        plt.savefig(os.path.join(output_folder, 'grafik_lamda_absorbansi.png'))

        # Tampilkan grafik
        plt.show()

    except Exception as e:
        messagebox.showerror("Error", f"Terjadi kesalahan: {e}")

def browse_folder():
    folder = filedialog.askdirectory(title="Pilih Folder CSV")
    if folder:
        folder_entry.delete(0, 'end')
        folder_entry.insert(0, folder)

def process_button_click():
    folder_path = folder_entry.get()
    sample_names = sample_names_entry.get().split(",")
    if not folder_path:
        messagebox.showerror("Error", "Folder belum dipilih!")
        return
    if not sample_names_entry.get():
        messagebox.showerror("Error", "Nama sampel belum diisi!")
        return
    process_data(folder_path, sample_names)

# Membuat GUI
root = Tk()
root.title("Program Analisis Absorbansi")

# Label dan input untuk folder CSV
Label(root, text="Folder CSV:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
folder_entry = Entry(root, width=50)
folder_entry.grid(row=0, column=1, padx=5, pady=5)
Button(root, text="Browse", command=browse_folder).grid(row=0, column=2, padx=5, pady=5)

# Label dan input untuk nama sampel
Label(root, text="Nama Sampel (pisahkan dengan koma):").grid(row=1, column=0, sticky="w", padx=5, pady=5)
sample_names_entry = Entry(root, width=50)
sample_names_entry.grid(row=1, column=1, columnspan=2, padx=5, pady=5)

# Tombol untuk memproses
Button(root, text="Proses", command=process_button_click, bg="green", fg="white").grid(row=2, column=0, columnspan=3, pady=10)

# Menjalankan GUI
root.mainloop()
