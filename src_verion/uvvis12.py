import os
import pandas as pd
import matplotlib.pyplot as plt
from tkinter import Tk, Label, Entry, Button, filedialog, messagebox, StringVar, Frame, Canvas, Scrollbar
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

# Fungsi untuk memproses data
def process_data():
    folder_path = folder_path_var.get()
    if not folder_path or not os.path.exists(folder_path):
        messagebox.showerror("Error", "Folder path tidak valid!")
        return

    sample_names = sample_names_var.get().split(',')
    sample_names = [name.strip() for name in sample_names]
    if not sample_names:
        messagebox.showerror("Error", "Nama sampel harus diisi!")
        return

    output_folder = "./GabunganAbsSampel"
    os.makedirs(output_folder, exist_ok=True)

    file_paths = [os.path.join(folder_path, file) for file in os.listdir(folder_path) if file.endswith('.csv')]

    if not file_paths:
        messagebox.showinfo("Info", "Tidak ada file CSV ditemukan di folder: " + folder_path)
        return

    data_frames = []
    for file_path in file_paths:
        df = pd.read_csv(file_path, skiprows=45, delimiter="\t", header=None)
        if df.shape[1] >= 3:
            df = df.iloc[:, :3]
        else:
            messagebox.showerror("Error", f"File {file_path} memiliki kurang dari 3 kolom!")
            return
        df = df.head(800)
        df.columns = ['Nomor', 'Lambda', 'Absorbansi']
        df = df.apply(pd.to_numeric, errors='coerce')
        data_frames.append(df)

    result = data_frames[0][['Nomor', 'Lambda']].copy()
    for i, df in enumerate(data_frames):
        result[f"Abs {sample_names[i]}"] = df['Absorbansi']
    output_file = os.path.join(output_folder, "AbsSampel.csv")
    result.to_csv(output_file, index=False)
    messagebox.showinfo("Sukses", f"File berhasil disimpan sebagai {output_file} di folder {output_folder}")

    # Plot data
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 8))
    plt.subplots_adjust(hspace=0.4)
    for i, df in enumerate(data_frames):
        ax1.plot(df['Lambda'], df['Absorbansi'], label=f"{sample_names[i]}")
        ax2.plot(df['Lambda'], 1 - df['Absorbansi'], label=f"Transmitansi {sample_names[i]}")
    ax1.set_title(graph_title_var.get() or "Absorbansi vs Panjang Gelombang")
    ax2.set_title("Transmitansi vs Panjang Gelombang")
    ax1.legend()
    ax2.legend()

    for widget in graph_frame.winfo_children():
        widget.destroy()

    canvas = FigureCanvasTkAgg(fig, master=graph_frame)
    canvas.draw()
    canvas.get_tk_widget().pack(fill="both", expand=True)

    toolbar = NavigationToolbar2Tk(canvas, graph_frame)
    toolbar.update()

# GUI Setup
root = Tk()
root.title("UV Vis Plotter from CSV")
root.geometry("800x600")

folder_path_var = StringVar()
sample_names_var = StringVar()
graph_title_var = StringVar()

# Input fields
Label(root, text="Folder Path:").grid(row=0, column=0, padx=10, pady=5, sticky="e")
Entry(root, textvariable=folder_path_var, width=50).grid(row=0, column=1, padx=10, pady=5)
Button(root, text="Browse", command=lambda: folder_path_var.set(filedialog.askdirectory())).grid(row=0, column=2, padx=10, pady=5)

Label(root, text="Sample Names:").grid(row=1, column=0, padx=10, pady=5, sticky="e")
Entry(root, textvariable=sample_names_var, width=50).grid(row=1, column=1, padx=10, pady=5)

Label(root, text="Graph Title:").grid(row=2, column=0, padx=10, pady=5, sticky="e")
Entry(root, textvariable=graph_title_var, width=50).grid(row=2, column=1, padx=10, pady=5)

Button(root, text="Process Data", command=process_data).grid(row=3, column=0, columnspan=3, pady=10)

# Graph frame
graph_frame = Frame(root)
graph_frame.grid(row=4, column=0, columnspan=3, sticky="nsew", padx=10, pady=10)

# Configure resizing behavior
root.grid_rowconfigure(4, weight=1)
root.grid_columnconfigure(1, weight=1)

root.mainloop()
