import os
import pandas as pd
import matplotlib.pyplot as plt
from tkinter import Tk, Label, Entry, Button, filedialog, messagebox, StringVar, Frame
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Fungsi untuk memproses data
def process_data():
    global canvas  # Agar bisa digunakan untuk menghapus grafik lama jika ada
    
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
    messagebox.showinfo("Sukses", f"File berhasil disimpan sebagai {output_file}")
    
    # Menghitung nilai absorbansi tertinggi dan degradasi bertahap
    abs_max_values = [df['Absorbansi'].max() for df in data_frames]
    degradasi_values = [(abs_max_values[0] - value) / abs_max_values[0] * 100 for value in abs_max_values[1:]]
    
    # Plot grafik
    fig, ax = plt.subplots(figsize=(10, 6))
    for i, df in enumerate(data_frames):
        ax.plot(df['Lambda'], df['Absorbansi'], label=f"{sample_names[i]}")
        abs_max_idx = df['Absorbansi'].idxmax()
        max_lambda = df['Lambda'].iloc[abs_max_idx]
        max_abs = df['Absorbansi'].iloc[abs_max_idx]
        ax.scatter(max_lambda, max_abs, color='red', zorder=5)
        ax.text(max_lambda, max_abs, f'{max_abs:.2f}', color='black', fontsize=9, ha='left', va='bottom')
    
    degradasi_text = '\n'.join([f'Degradasi {sample_names[0]} ke {sample_names[i+1]}: {degradasi_values[i]:.2f}%' 
                                for i in range(len(degradasi_values))])
    ax.text(0.05, 0.95, degradasi_text, transform=ax.transAxes,
            fontsize=9, color='black', ha='left', va='top', bbox=dict(facecolor='white', edgecolor='black', boxstyle='round,pad=0.25'))
    
    ax.set_xlabel('Lambda (nm)')
    ax.set_ylabel('Absorbansi')
    ax.set_title('Hubungan Lambda dengan Absorbansi')
    ax.legend()
    ax.grid(True)
    
    # Hapus canvas sebelumnya jika ada
    if canvas:
        canvas.get_tk_widget().destroy()
    
    # Tampilkan grafik di GUI
    canvas = FigureCanvasTkAgg(fig, master=graph_frame)
    canvas.draw()
    canvas.get_tk_widget().pack()

# Fungsi untuk memilih folder
def select_folder():
    folder = filedialog.askdirectory()
    folder_path_var.set(folder)

# GUI Setup
root = Tk()
root.title("UV-Vis Data Processor")

# Variabel global untuk canvas
canvas = None

# Input folder path
Label(root, text="Folder Path:").grid(row=0, column=0, padx=10, pady=5, sticky="w")
folder_path_var = StringVar()
Entry(root, textvariable=folder_path_var, width=50).grid(row=0, column=1, padx=10, pady=5)
Button(root, text="Browse", command=select_folder).grid(row=0, column=2, padx=10, pady=5)

# Input sample names
Label(root, text="Sample Names (comma-separated):").grid(row=1, column=0, padx=10, pady=5, sticky="w")
sample_names_var = StringVar()
Entry(root, textvariable=sample_names_var, width=50).grid(row=1, column=1, padx=10, pady=5)

# Process button
Button(root, text="Process Data", command=process_data).grid(row=2, column=0, columnspan=3, pady=10)

# Frame untuk grafik
graph_frame = Frame(root)
graph_frame.grid(row=3, column=0, columnspan=3, pady=10)

# Start GUI loop
root.mainloop()
