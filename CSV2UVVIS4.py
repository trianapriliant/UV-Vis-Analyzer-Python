import os
import pandas as pd
import matplotlib.pyplot as plt
from tkinter import Tk, Label, Entry, Button, filedialog, messagebox, StringVar, Frame, Radiobutton, IntVar
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

# Fungsi untuk memproses data
def process_data():
    global canvas, toolbar  # Variabel global untuk canvas dan toolbar
    
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
    
    # Ambil judul grafik dari input
    graph_title = graph_title_var.get()
    if not graph_title:
        messagebox.showerror("Error", "Judul grafik harus diisi!")
        return
    
    # Tentukan alat yang dipilih (lama atau baru)
    alat_terpilih = alat_var.get()  # 1 = Alat Lama, 2 = Alat Baru
    
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
    all_transmitansi = []
    
    for file_path in file_paths:
        if alat_terpilih == 1:  # Alat Lama
            df = pd.read_csv(file_path, skiprows=45, delimiter="\t", header=None)
            if df.shape[1] >= 3:
                df = df.iloc[:, :3]
            else:
                messagebox.showerror("Error", f"File {file_path} memiliki kurang dari 3 kolom!")
                return
            
            df.columns = ['Nomor', 'Lambda', 'Absorbansi']
        else:  # Alat Baru
            df = pd.read_csv(file_path, delimiter=";")
            if df.shape[1] >= 2:
                df = df.iloc[:, :2]
            else:
                messagebox.showerror("Error", f"File {file_path} memiliki kurang dari 2 kolom!")
                return
            
            df.columns = ['Lambda', 'Absorbansi']
            df['Nomor'] = range(1, len(df) + 1)  # Tambahkan kolom Nomor
        
        df['Lambda'] = pd.to_numeric(df['Lambda'], errors='coerce')
        df['Absorbansi'] = pd.to_numeric(df['Absorbansi'], errors='coerce')
        
        # Hitung Transmitansi (jika diperlukan)
        df['Transmitansi'] = 10 ** (-df['Absorbansi'])  # Transmitansi = 10^(-Absorbansi)
        
        data_frames.append(df)
        all_lambda.append(df['Lambda'])
        all_absorbansi.append(df['Absorbansi'])
        all_transmitansi.append(df['Transmitansi'])
    
    result = data_frames[0][['Nomor', 'Lambda']].copy()
    for i, df in enumerate(data_frames):
        result[f"Abs {sample_names[i]}"] = df['Absorbansi']
        result[f"Trans {sample_names[i]}"] = df['Transmitansi']
    
    output_file = os.path.join(output_folder, "AbsSampel.csv")
    result.to_csv(output_file, index=False)
    messagebox.showinfo("Sukses", f"File berhasil disimpan sebagai {output_file}")
    
    # Menghitung nilai absorbansi tertinggi dan degradasi bertahap
    abs_max_values = [df['Absorbansi'].max() for df in data_frames]
    degradasi_values = [(abs_max_values[0] - value) / abs_max_values[0] * 100 for value in abs_max_values[1:]]
    
    # Fungsi untuk menampilkan grafik
    def plot_graph(show_absorbance=True):
        global canvas, toolbar  # Menggunakan variabel global
        
        # Hapus canvas dan toolbar sebelumnya jika ada
        if canvas:
            canvas.get_tk_widget().pack_forget()
        if toolbar:
            toolbar.pack_forget()
        
        # Buat grafik baru
        fig, ax = plt.subplots(figsize=(10, 6))
        for i, df in enumerate(data_frames):
            if show_absorbance:
                ax.plot(df['Lambda'], df['Absorbansi'], label=f"{sample_names[i]} (Absorbansi)")
                abs_max_idx = df['Absorbansi'].idxmax()
                max_lambda = df['Lambda'].iloc[abs_max_idx]
                max_abs = df['Absorbansi'].iloc[abs_max_idx]
                ax.scatter(max_lambda, max_abs, color='black', zorder=1, s=2)
                ax.text(max_lambda, max_abs, f'{max_abs:.2f}', color='black', fontsize=8, ha='left', va='bottom')
                ax.legend(fontsize=6)
            else:
                ax.plot(df['Lambda'], df['Transmitansi'], label=f"{sample_names[i]} (Transmitansi)")
        
        degradasi_text = '\n'.join([f'% Degradasi {sample_names[0]} ke {sample_names[i+1]} Jam: {degradasi_values[i]:.2f}%' 
                                    for i in range(len(degradasi_values))])
        ax.text(0.05, 0.95, degradasi_text, transform=ax.transAxes,
                fontsize=9, color='black', ha='left', va='top', bbox=dict(facecolor='white', edgecolor='black', boxstyle='round,pad=0.25'))
        
        # Set label sumbu x dan y
        ax.set_xlabel('Panjang Gelombang (nm)')  # Sumbu x
        ax.set_ylabel('Absorbansi' if show_absorbance else 'Transmitansi')  # Sumbu y
        ax.set_title(graph_title)  # Judul grafik dari input pengguna
        ax.legend()
        ax.grid(True)
        
        # Tampilkan grafik di GUI
        canvas = FigureCanvasTkAgg(fig, master=graph_frame)
        canvas.draw()
        canvas.get_tk_widget().pack()
        
        # Tambahkan toolbar interaktif
        toolbar = NavigationToolbar2Tk(canvas, graph_frame)
        toolbar.update()
        toolbar.pack()
    
    # Tampilkan grafik berdasarkan pilihan pengguna
    if plot_type.get() == 1:  # 1 = Absorbansi
        plot_graph(show_absorbance=True)
    else:  # 2 = Transmitansi
        plot_graph(show_absorbance=False)

# Fungsi untuk memilih folder
def select_folder():
    folder = filedialog.askdirectory()
    folder_path_var.set(folder)

# Fungsi untuk menutup aplikasi dengan benar
def on_close():
    root.quit()  # Berhenti dari loop utama tkinter

# GUI Setup
root = Tk()
root.title("Absorbance Plot UV-Vis")

# Variabel global untuk canvas dan toolbar
canvas = None
toolbar = None

# Input folder path
Label(root, text="Folder Path:").grid(row=0, column=0, padx=10, pady=5, sticky="w")
folder_path_var = StringVar()
Entry(root, textvariable=folder_path_var, width=50).grid(row=0, column=1, padx=10, pady=5)
Button(root, text="Browse", command=select_folder).grid(row=0, column=2, padx=10, pady=5)

# Input sample names
Label(root, text="Sample Names (Comma-Separated):").grid(row=1, column=0, padx=10, pady=5, sticky="w")
sample_names_var = StringVar()
Entry(root, textvariable=sample_names_var, width=50).grid(row=1, column=1, padx=10, pady=5)

# Input judul grafik
Label(root, text="Graph Title:").grid(row=2, column=0, padx=10, pady=5, sticky="w")
graph_title_var = StringVar()
Entry(root, textvariable=graph_title_var, width=50).grid(row=2, column=1, padx=10, pady=5)

# Radio button untuk memilih alat
Label(root, text="Pilih Alat:").grid(row=3, column=0, padx=10, pady=5, sticky="w")
alat_var = IntVar(value=1)  # 1 = Alat Lama, 2 = Alat Baru
Radiobutton(root, text="Alat Lama", variable=alat_var, value=1).grid(row=3, column=1, padx=10, pady=5, sticky="w")
Radiobutton(root, text="Alat Baru", variable=alat_var, value=2).grid(row=3, column=2, padx=10, pady=5, sticky="w")

# Radio button untuk memilih jenis grafik
Label(root, text="Pilih Jenis Grafik:").grid(row=4, column=0, padx=10, pady=5, sticky="w")
plot_type = IntVar(value=1)  # 1 = Absorbansi, 2 = Transmitansi
Radiobutton(root, text="Absorbansi", variable=plot_type, value=1).grid(row=4, column=1, padx=10, pady=5, sticky="w")
Radiobutton(root, text="Transmitansi", variable=plot_type, value=2).grid(row=4, column=2, padx=10, pady=5, sticky="w")

# Process button
Button(root, text="Process Data", command=process_data).grid(row=5, column=0, columnspan=3, pady=10)

# Frame untuk grafik
graph_frame = Frame(root)
graph_frame.grid(row=6, column=0, columnspan=3, pady=10)

# Tambahkan label untuk credit
credit_label = Label(
    root, 
    text="made with ❤️ by rynn ~ personal use for physics of materials", 
    font=("Segoe UI Emoji", 8),  # Gunakan font yang mendukung emoji
    fg="gray"  # 
)
credit_label.grid(row=7, column=0, columnspan=3, pady=5)

# Menangani penutupan jendela
root.protocol("WM_DELETE_WINDOW", on_close)

# Start GUI loop
root.mainloop()