import os
import pandas as pd
import matplotlib.pyplot as plt
from tkinter import Tk, Label, Entry, Button, filedialog, messagebox, StringVar, Frame
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import threading

# Fungsi untuk memproses data
def process_data():
    global canvas, toolbar  # Agar bisa digunakan untuk menghapus grafik dan toolbar lama jika ada
    
    # Ambil path folder dari input
    folder_path = folder_path_var.get()
    if not folder_path or not os.path.exists(folder_path):
        messagebox.showerror("Error", "Folder path tidak valid!")
        return
    
    # Ambil nama-nama sampel dari input
    sample_names = sample_names_var.get().split(',')
    sample_names = [name.strip() for name in sample_names]
    if not sample_names or len(sample_names) == 0:
        messagebox.showerror("Error", "Nama sampel harus diisi!")
        return
    
    output_folder = "./GabunganAbsSampel"
    os.makedirs(output_folder, exist_ok=True)  # Membuat folder hasil jika belum ada
    
    # Ambil semua file CSV di folder
    file_paths = [os.path.join(folder_path, file) for file in os.listdir(folder_path) if file.endswith('.csv')]
    
    if not file_paths:
        messagebox.showinfo("Info", "Tidak ada file CSV ditemukan di folder: " + folder_path)
        return
    
    data_frames = []
    all_lambda = []
    all_absorbansi = []
    
    for file_path in file_paths:
        df = pd.read_csv(file_path, skiprows=45, delimiter="\t", header=None)
        if df.shape[1] >= 3:
            df = df.iloc[:, :3]
        else:
            messagebox.showerror("Error", f"File {file_path} memiliki kurang dari 3 kolom!")
            return
        
        df = df.head(800)
        df.columns = ['Nomor', 'Lambda', 'Absorbansi']
        df['Nomor'] = pd.to_numeric(df['Nomor'], errors='coerce')
        df['Lambda'] = pd.to_numeric(df['Lambda'], errors='coerce')
        df['Absorbansi'] = pd.to_numeric(df['Absorbansi'], errors='coerce')
        
        data_frames.append(df)
        all_lambda.append(df['Lambda'])
        all_absorbansi.append(df['Absorbansi'])
    
    result = data_frames[0][['Nomor', 'Lambda']].copy()
    for i, df in enumerate(data_frames):
        result[f"Abs {sample_names[i]}"] = df['Absorbansi']
    
    output_file = os.path.join(output_folder, "AbsSampel.csv")
    result.to_csv(output_file, index=False)
    messagebox.showinfo("Sukses", f"File berhasil disimpan sebagai {output_file} di folder {output_folder} ")
    
    # Menghitung nilai absorbansi tertinggi dan degradasi bertahap
    abs_max_values = [df['Absorbansi'].max() for df in data_frames]
    degradasi_values = [(abs_max_values[0] - value) / abs_max_values[0] * 100 for value in abs_max_values[1:]]
    
    # Menghitung Transmitansi (R = 1 - Absorbansi)
    reflectance_values = [1 - df['Absorbansi'] for df in data_frames]
    
    # Ambil judul grafik dari input pengguna
    graph_title = graph_title_var.get() if graph_title_var.get() else "Hubungan Panjang Gelombang dengan Absorbansi dan Transmitansi"
    
    # Plot grafik dalam format kanan-kiri
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 6))  # Mengubah layout menjadi kolom
    plt.subplots_adjust(wspace=0.2)
    
    # Grafik Absorbansi
    for i, df in enumerate(data_frames):
        ax1.plot(df['Lambda'], df['Absorbansi'], label=f"{sample_names[i]}")
        abs_max_idx = df['Absorbansi'].idxmax()
        max_lambda = df['Lambda'].iloc[abs_max_idx]
        max_abs = df['Absorbansi'].iloc[abs_max_idx]
        ax1.scatter(max_lambda, max_abs, color='black', zorder=0, s=10)
        ax1.text(max_lambda + 1, max_abs, f'{max_abs:.2f}', color='black', fontsize=8, ha='left', va='bottom')
    
    degradasi_text = '\n'.join([f'Degradasi {sample_names[0]} ke {sample_names[i+1]}: {degradasi_values[i]:.2f}%' 
                                for i in range(len(degradasi_values))])
    ax1.text(0.05, 0.95, degradasi_text, transform=ax1.transAxes,
            fontsize=8, color='black', ha='left', va='top', bbox=dict(facecolor='white', edgecolor='black', boxstyle='round,pad=0.25'))
    
    ax1.set_xlabel('Panjang Gelombang (nm)')
    ax1.set_ylabel('Absorbansi')
    ax1.set_title(graph_title)  # Menggunakan judul yang dimasukkan oleh pengguna
    ax1.legend()
    ax1.grid(True)
    
    # Grafik Transmitansi
    for i, reflectance in enumerate(reflectance_values):
        ax2.plot(data_frames[i]['Lambda'], reflectance, label=f"Transmitansi {sample_names[i]}")
    
    ax2.set_xlabel('Panjang Gelombang (nm)')
    ax2.set_ylabel('Transmitansi')
    ax2.set_title("Panjang Gelombang vs Transmitansi")
    ax2.legend()
    ax2.grid(True)
    
    # Hapus canvas dan toolbar sebelumnya jika ada
    if canvas:
        canvas.get_tk_widget().destroy()
    if toolbar:
        toolbar.destroy()
    
    # Tampilkan grafik di GUI
    canvas = FigureCanvasTkAgg(fig, master=graph_frame)
    canvas.draw()
    canvas.get_tk_widget().pack()
    
    # Tambahkan toolbar interaktif
    toolbar = NavigationToolbar2Tk(canvas, graph_frame)
    toolbar.update()
    toolbar.pack()

# Fungsi untuk memilih folder
def select_folder():
    folder = filedialog.askdirectory()
    folder_path_var.set(folder)

# Fungsi untuk menutup aplikasi dengan benar
def on_close():
    root.quit()  # Berhenti dari loop utama tkinter

# GUI Setup
root = Tk()
root.title("UV Vis Plotter from CSV")

# Variabel global untuk canvas dan toolbar
canvas = None
toolbar = None

# Input folder path
Label(root, text="Folder Path:").grid(row=0, column=0, padx=10, pady=5, sticky="w")
folder_path_var = StringVar()
Entry(root, textvariable=folder_path_var, width=50).grid(row=0, column=1, padx=10, pady=5)
Button(root, text="Browse", command=select_folder).grid(row=0, column=2, padx=10, pady=5)

# Input sample names
Label(root, text="Sample Names (comma-separated):").grid(row=1, column=0, padx=10, pady=5, sticky="w")
sample_names_var = StringVar()
Entry(root, textvariable=sample_names_var, width=50).grid(row=1, column=1, padx=10, pady=5)

# Input untuk judul grafik
Label(root, text="Graph Title:").grid(row=2, column=0, padx=10, pady=5, sticky="w")
graph_title_var = StringVar()
Entry(root, textvariable=graph_title_var, width=50).grid(row=2, column=1, padx=10, pady=5)

# Process button
Button(root, text="Process Data", command=process_data).grid(row=3, column=0, columnspan=3, pady=10)

# Frame untuk grafik
graph_frame = Frame(root)
graph_frame.grid(row=4, column=0, columnspan=3, pady=10)

# Tambahkan label untuk credit
credit_label = Label(root, text="v0.1 | made with ❤️ by rynn ~ personal use for physics of materials", font=("Arial", 8), fg="gray")
credit_label.grid(row=5, column=0, columnspan=3, pady=5)

# Menangani penutupan jendela
root.protocol("WM_DELETE_WINDOW", on_close)

# Start GUI loop
root.mainloop()
