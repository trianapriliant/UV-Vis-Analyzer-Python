import os
import pandas as pd
import matplotlib.pyplot as plt
from tkinter import Tk, Label, Entry, Button, filedialog, messagebox, StringVar, Frame, Radiobutton, IntVar, Scale
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

# Fungsi untuk memproses data
def process_data():
    global canvas, toolbar
    folder_path = folder_path_var.get()
    if not folder_path or not os.path.exists(folder_path):
        messagebox.showerror("Error", "Folder path tidak valid!")
        return
    
    sample_names = sample_names_var.get().split(',')
    sample_names = [name.strip() for name in sample_names if name.strip()]  # Hapus elemen kosong
    if not sample_names:
        messagebox.showerror("Error", "Nama sampel harus diisi!")
        return
    
    graph_title = graph_title_var.get()
    if not graph_title:
        messagebox.showerror("Error", "Judul grafik harus diisi!")
        return
    
    alat_terpilih = alat_var.get()
    output_folder = "./GabunganAbsSampel"
    os.makedirs(output_folder, exist_ok=True)
    
    file_paths = [os.path.join(folder_path, file) for file in os.listdir(folder_path) if file.endswith('.csv')]
    
    if not file_paths:
        messagebox.showinfo("Info", "Tidak ada file CSV ditemukan di folder: " + folder_path)
        return
    
    data_frames = []
    for file_path in file_paths:
        if alat_terpilih == 1:
            df = pd.read_csv(file_path, skiprows=45, delimiter="\t", header=None)
            if df.shape[1] >= 3:
                df = df.iloc[:, :3]
            else:
                messagebox.showerror("Error", f"File {file_path} memiliki kurang dari 3 kolom!, coba pilih alat lain")
                return
            df.columns = ['Nomor', 'Lambda', 'Absorbansi']
        else:
            df = pd.read_csv(file_path, delimiter=";")
            if df.shape[1] >= 2:
                df = df.iloc[:, :2]
            else:
                messagebox.showerror("Error", f"File {file_path} memiliki kurang dari 2 kolom!, coba pilih alat lain")
                return
            df.columns = ['Lambda', 'Absorbansi']
            df['Nomor'] = range(1, len(df) + 1)
        
        df['Lambda'] = pd.to_numeric(df['Lambda'], errors='coerce')
        df['Absorbansi'] = pd.to_numeric(df['Absorbansi'], errors='coerce')
        df['Transmitansi'] = 10 ** (-df['Absorbansi'])
        data_frames.append(df)
    
    result = data_frames[0][['Nomor', 'Lambda']].copy()
    for i, df in enumerate(data_frames):
        result[f"Abs {sample_names[i]}"] = df['Absorbansi']
        result[f"Trans {sample_names[i]}"] = df['Transmitansi']
    
    output_file = os.path.join(output_folder, "AbsSampel.csv")
    result.to_csv(output_file, index=False)
    messagebox.showinfo("Sukses", f"File berhasil disimpan sebagai {output_file}")
    
    abs_max_values = [df['Absorbansi'].max() for df in data_frames]
    degradasi_values = [(abs_max_values[0] - value) / abs_max_values[0] * 100 for value in abs_max_values[1:]]
    
    def plot_graph(show_absorbance=True):
        global canvas, toolbar
        if canvas:
            canvas.get_tk_widget().pack_forget()
        if toolbar:
            toolbar.pack_forget()
        
        figsize = (fig_width_scale.get(), fig_height_scale.get())
        fig, ax = plt.subplots(figsize=figsize)
        for i, df in enumerate(data_frames):
            if show_absorbance:
                ax.plot(df['Lambda'], df['Absorbansi'], label=f"{sample_names[i]} (Absorbansi)")
                abs_max_idx = df['Absorbansi'].idxmax()
                max_lambda = df['Lambda'].iloc[abs_max_idx]
                max_abs = df['Absorbansi'].iloc[abs_max_idx]
                ax.scatter(max_lambda, max_abs, color='black', zorder=1, s=2)
                ax.text(max_lambda, max_abs, f'{max_abs:.2f}', color='black', fontsize=8, ha='left', va='bottom')
            else:
                ax.plot(df['Lambda'], df['Transmitansi'], label=f"{sample_names[i]} (Transmitansi)")
        
        degradasi_text = '\n'.join([f'% Degradasi {sample_names[0]} ke {sample_names[i+1]} Jam: {degradasi_values[i]:.2f}%' 
                                    for i in range(len(degradasi_values))])
        ax.text(0.05, 0.95, degradasi_text, transform=ax.transAxes,
                fontsize=8, color='black', ha='left', va='top', bbox=dict(facecolor='white', edgecolor='black', boxstyle='round,pad=0.25'))
        ax.set_xlabel('Panjang Gelombang (nm)')
        ax.set_ylabel('Absorbansi' if show_absorbance else 'Transmitansi')
        ax.set_title(graph_title)
        ax.legend(fontsize=8)
        ax.grid(True)
        
        canvas = FigureCanvasTkAgg(fig, master=graph_frame)
        canvas.draw()
        canvas.get_tk_widget().pack()
        
        toolbar = NavigationToolbar2Tk(canvas, graph_frame)
        toolbar.update()
        toolbar.pack()
    
    if plot_type.get() == 1:
        plot_graph(show_absorbance=True)
    else:
        plot_graph(show_absorbance=False)

def select_folder():
    folder = filedialog.askdirectory()
    folder_path_var.set(folder)

def on_entry_click(event):
    """Fungsi yang dipanggil ketika Entry diklik."""
    if sample_names_entry.get() == "Pisahkan dengan koma":
        sample_names_entry.delete(0, "end")  # Hapus placeholder
        sample_names_entry.config(fg="black")  # Ubah warna teks ke hitam

def on_focus_out(event):
    """Fungsi yang dipanggil ketika focus keluar dari Entry."""
    if sample_names_entry.get() == "":
        sample_names_entry.insert(0, "Pisahkan dengan koma")  # Tambahkan placeholder
        sample_names_entry.config(fg="grey")  # Ubah warna teks ke abu-abu

def on_close():
    root.quit()

# GUI Setup
root = Tk()
root.title("Absorbance Plot UV-Vis")

canvas = None
toolbar = None

# Frame untuk input
input_frame = Frame(root)
input_frame.grid(row=0, column=0, padx=10, pady=5, sticky="w")

Label(input_frame, text="Folder Path:").grid(row=0, column=0, padx=5, pady=2, sticky="w")
folder_path_var = StringVar()
Entry(input_frame, textvariable=folder_path_var, width=30).grid(row=0, column=1, padx=5, pady=2)
Button(input_frame, text="Browse", command=select_folder).grid(row=0, column=2, padx=5, pady=2)

Label(input_frame, text="Sample Names:").grid(row=1, column=0, padx=5, pady=2, sticky="w")
sample_names_var = StringVar()
sample_names_entry = Entry(input_frame, textvariable=sample_names_var, width=30, fg="grey")
sample_names_entry.grid(row=1, column=1, padx=5, pady=2)
sample_names_entry.insert(0, "Pisahkan dengan koma")  # Tambahkan placeholder
sample_names_entry.bind("<FocusIn>", on_entry_click)  # Ketika Entry diklik
sample_names_entry.bind("<FocusOut>", on_focus_out)   # Ketika focus keluar dari Entry

Label(input_frame, text="Graph Title:").grid(row=2, column=0, padx=5, pady=2, sticky="w")
graph_title_var = StringVar()
Entry(input_frame, textvariable=graph_title_var, width=30).grid(row=2, column=1, padx=5, pady=2)

Label(input_frame, text="Pilih Alat:").grid(row=3, column=0, padx=5, pady=2, sticky="w")
alat_var = IntVar(value=1)
Radiobutton(input_frame, text="Alat Lama", variable=alat_var, value=1).grid(row=3, column=1, padx=5, pady=2, sticky="w")
Radiobutton(input_frame, text="Alat Baru", variable=alat_var, value=2).grid(row=3, column=2, padx=5, pady=2, sticky="w")

Label(input_frame, text="Pilih Jenis Grafik:").grid(row=4, column=0, padx=5, pady=2, sticky="w")
plot_type = IntVar(value=1)
Radiobutton(input_frame, text="Absorbansi", variable=plot_type, value=1).grid(row=4, column=1, padx=5, pady=2, sticky="w")
Radiobutton(input_frame, text="Transmitansi", variable=plot_type, value=2).grid(row=4, column=2, padx=5, pady=2, sticky="w")

Label(input_frame, text="Lebar Grafik:").grid(row=5, column=0, padx=5, pady=2, sticky="w")
fig_width_scale = Scale(input_frame, from_=4, to=20, orient="horizontal")
fig_width_scale.set(8)
fig_width_scale.grid(row=5, column=1, padx=5, pady=2, sticky="w")

Label(input_frame, text="Tinggi Grafik:").grid(row=5, column=2, padx=5, pady=2, sticky="w")
fig_height_scale = Scale(input_frame, from_=2, to=16, orient="horizontal")
fig_height_scale.set(4)
fig_height_scale.grid(row=5, column=3, padx=5, pady=2, sticky="w")

Button(input_frame, text="Process Data", command=process_data).grid(row=7, column=0, columnspan=4, pady=5)

# Frame untuk grafik
graph_frame = Frame(root)
graph_frame.grid(row=1, column=0, padx=10, pady=5, sticky="nsew")

credit_label = Label(
    root, 
    text="v1.4 | made with ❤️ by rynn ~ personal use for physics of materials", 
    font=("Segoe UI Emoji", 8),
    fg="gray"
)
credit_label.grid(row=2, column=0, padx=10, pady=5, sticky="w")

root.protocol("WM_DELETE_WINDOW", on_close)
root.mainloop()