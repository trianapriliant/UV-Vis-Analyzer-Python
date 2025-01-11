import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from tkinter import Tk, Label, Entry, Button, filedialog, messagebox, StringVar, Frame, Radiobutton, IntVar, Scale, Checkbutton, Menu
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from scipy.optimize import curve_fit


class UVVisAnalyzer:
    def __init__(self, root):
        self.root = root
        self.root.title("Absorbance Plot UV-Vis")
        self.data_frames = None
        self.degradasi_values = None
        self.canvas = None
        self.toolbar = None

        # Inisialisasi GUI
        self.setup_gui()

    def setup_gui(self):
        # Membuat Menu
        menu_bar = Menu(self.root)
        self.root.config(menu=menu_bar)

        # Menu Analisis
        analisis_menu = Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="Analisis", menu=analisis_menu)
        analisis_menu.add_command(label="Kinetika Degradasi", command=self.kinetika_degradasi)
        analisis_menu.add_command(label="Konsentrasi Relatif", command=self.konsentrasi_relatif)

        # Frame untuk input
        input_frame = Frame(self.root)
        input_frame.grid(row=0, column=0, padx=10, pady=5, sticky="w")

        # Folder Path
        Label(input_frame, text="Folder Path:").grid(row=0, column=0, padx=5, pady=2, sticky="w")
        self.folder_path_var = StringVar()
        self.folder_path_entry = Entry(input_frame, textvariable=self.folder_path_var, width=40, fg="grey")
        self.folder_path_entry.grid(row=0, column=1, padx=5, pady=2)
        self.folder_path_entry.insert(0, "folder berisi file-file csv")
        self.folder_path_entry.bind("<FocusIn>", self.on_entry_click_folder)
        self.folder_path_entry.bind("<FocusOut>", self.on_focus_out_folder)
        Button(input_frame, text="Browse", command=self.select_folder).grid(row=0, column=2, padx=5, pady=2)

        # Sample Names
        Label(input_frame, text="Sample Names:").grid(row=1, column=0, padx=5, pady=2, sticky="w")
        self.sample_names_var = StringVar()
        self.sample_names_entry = Entry(input_frame, textvariable=self.sample_names_var, width=40, fg="grey")
        self.sample_names_entry.grid(row=1, column=1, padx=5, pady=2)
        self.sample_names_entry.insert(0, "pisahkan nama-nama sampel dengan koma")
        self.sample_names_entry.bind("<FocusIn>", self.on_entry_click)
        self.sample_names_entry.bind("<FocusOut>", self.on_focus_out)

        # Graph Title
        Label(input_frame, text="Graph Title:").grid(row=2, column=0, padx=5, pady=2, sticky="w")
        self.graph_title_var = StringVar()
        Entry(input_frame, textvariable=self.graph_title_var, width=40).grid(row=2, column=1, padx=5, pady=2)

        # Pilih Alat
        Label(input_frame, text="Pilih Alat:").grid(row=3, column=0, padx=5, pady=2, sticky="w")
        self.alat_var = IntVar(value=1)
        Radiobutton(input_frame, text="Alat Lama", variable=self.alat_var, value=1).grid(row=3, column=1, padx=5, pady=2, sticky="w")
        Radiobutton(input_frame, text="Alat Baru", variable=self.alat_var, value=2).grid(row=3, column=2, padx=5, pady=2, sticky="w")

        # Pilih Jenis Grafik
        Label(input_frame, text="Pilih Jenis Grafik:").grid(row=4, column=0, padx=5, pady=0, sticky="w")
        self.plot_type = IntVar(value=1)
        Radiobutton(input_frame, text="Absorbansi", variable=self.plot_type, value=1).grid(row=4, column=1, padx=5, pady=0, sticky="w")
        Radiobutton(input_frame, text="Transmitansi", variable=self.plot_type, value=2).grid(row=4, column=2, padx=5, pady=0, sticky="w")

        # Lebar dan Tinggi Grafik
        Label(input_frame, text="Lebar Grafik:").grid(row=5, column=0, padx=5, pady=2, sticky="w")
        self.fig_width_scale = Scale(input_frame, from_=4, to=20, orient="horizontal")
        self.fig_width_scale.set(8)
        self.fig_width_scale.grid(row=5, column=1, padx=5, pady=2, sticky="w")

        Label(input_frame, text="Tinggi Grafik:").grid(row=5, column=2, padx=5, pady=2, sticky="w")
        self.fig_height_scale = Scale(input_frame, from_=2, to=16, orient="horizontal")
        self.fig_height_scale.set(4)
        self.fig_height_scale.grid(row=5, column=3, padx=5, pady=2, sticky="w")

        # Checkbuttons
        self.show_degradasi = IntVar(value=1)
        Checkbutton(input_frame, text="% Degradasi", variable=self.show_degradasi).grid(row=6, column=0, sticky="ew", padx=2, pady=2)
        self.show_peak_points = IntVar(value=1)
        Checkbutton(input_frame, text="Titik Puncak", variable=self.show_peak_points).grid(row=6, column=1, sticky="ew", padx=2, pady=2)
        self.show_legend = IntVar(value=1)
        Checkbutton(input_frame, text="Legend", variable=self.show_legend).grid(row=6, column=2, sticky="ew", padx=2, pady=2)

        # Tombol Process Data
        Button(input_frame, text="Process Data", command=self.process_data).grid(row=9, column=0, columnspan=4, pady=5)

        # Frame untuk grafik
        self.graph_frame = Frame(self.root)
        self.graph_frame.grid(row=1, column=0, padx=10, pady=5, sticky="nsew")

        # Credit Label
        credit_label = Label(
            self.root,
            text="v1.5 | made with ❤️ by rynn ~ personal use for physics of materials",
            font=("Segoe UI Emoji", 8),
            fg="gray"
        )
        credit_label.grid(row=2, column=0, padx=10, pady=5, sticky="w")

        # Handle window close
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def select_folder(self):
        folder = filedialog.askdirectory()
        self.folder_path_var.set(folder)

    def on_entry_click_folder(self, event):
        if self.folder_path_entry.get() == "folder berisi file-file csv":
            self.folder_path_entry.delete(0, "end")
            self.folder_path_entry.config(fg="black")

    def on_focus_out_folder(self, event):
        if self.folder_path_entry.get() == "":
            self.folder_path_entry.insert(0, "folder berisi file-file csv")
            self.folder_path_entry.config(fg="grey")

    def on_entry_click(self, event):
        if self.sample_names_entry.get() == "pisahkan nama-nama sampel dengan koma":
            self.sample_names_entry.delete(0, "end")
            self.sample_names_entry.config(fg="black")

    def on_focus_out(self, event):
        if self.sample_names_entry.get() == "":
            self.sample_names_entry.insert(0, "pisahkan nama-nama sampel dengan koma")
            self.sample_names_entry.config(fg="grey")

    def on_close(self):
        self.root.quit()

    def process_data(self):
        folder_path = self.folder_path_var.get()
        if not folder_path or not os.path.exists(folder_path):
            messagebox.showerror("Error", "Folder path tidak valid!")
            return

        sample_names = self.sample_names_var.get().split(',')
        sample_names = [name.strip() for name in sample_names if name.strip()]
        if not sample_names:
            messagebox.showerror("Error", "Nama sampel harus diisi!")
            return

        graph_title = self.graph_title_var.get()
        if not graph_title:
            messagebox.showerror("Error", "Judul grafik harus diisi!")
            return

        alat_terpilih = self.alat_var.get()
        output_folder = "./GabunganAbsSampel"
        os.makedirs(output_folder, exist_ok=True)

        file_paths = [os.path.join(folder_path, file) for file in os.listdir(folder_path) if file.endswith('.csv')]
        if not file_paths:
            messagebox.showinfo("Info", "Tidak ada file CSV ditemukan di folder: " + folder_path)
            return

        self.data_frames = []
        for file_path in file_paths:
            try:
                if alat_terpilih == 1:
                    df = pd.read_csv(file_path, skiprows=45, delimiter="\t", header=None)
                    if df.shape[1] >= 3:
                        df = df.iloc[:, :3]
                    else:
                        messagebox.showerror("Error", f"File {file_path} memiliki csv dengan format berbeda, coba pilih alat lain")
                        return
                    df.columns = ['Nomor', 'Lambda', 'Absorbansi']
                else:
                    df = pd.read_csv(file_path, delimiter=";")
                    if df.shape[1] >= 2:
                        df = df.iloc[:, :2]
                    else:
                        messagebox.showerror("Error", f"File {file_path} memiliki csv dengan format berbeda, coba pilih alat lain")
                        return
                    df.columns = ['Lambda', 'Absorbansi']
                    df['Nomor'] = range(1, len(df) + 1)

                df['Lambda'] = pd.to_numeric(df['Lambda'], errors='coerce')
                df['Absorbansi'] = pd.to_numeric(df['Absorbansi'], errors='coerce')
                df['Transmitansi'] = 10 ** (-df['Absorbansi'])
                self.data_frames.append(df)
            except Exception as e:
                messagebox.showerror("Error", f"Gagal membaca file {file_path}: {str(e)}")
                return

        result = self.data_frames[0][['Nomor', 'Lambda']].copy()
        for i, df in enumerate(self.data_frames):
            result[f"Abs {sample_names[i]}"] = df['Absorbansi']
            result[f"Trans {sample_names[i]}"] = df['Transmitansi']

        output_file = os.path.join(output_folder, "AbsSampel.csv")
        result.to_csv(output_file, index=False)
        messagebox.showinfo("Sukses", f"File berhasil disimpan sebagai {output_file}")

        # Hitung nilai degradasi
        abs_max_values = [df['Absorbansi'].max() for df in self.data_frames]
        self.degradasi_values = [(abs_max_values[0] - value) / abs_max_values[0] * 100 for value in abs_max_values[1:]]

        # Plot grafik
        self.plot_graph(show_absorbance=self.plot_type.get() == 1)

    def plot_graph(self, show_absorbance=True):
        if self.canvas:
            self.canvas.get_tk_widget().pack_forget()
        if self.toolbar:
            self.toolbar.pack_forget()

        figsize = (self.fig_width_scale.get(), self.fig_height_scale.get())
        fig, ax = plt.subplots(figsize=figsize)
        for i, df in enumerate(self.data_frames):
            if show_absorbance:
                ax.plot(df['Lambda'], df['Absorbansi'], label=f"{self.sample_names_var.get().split(',')[i].strip()} (Absorbansi)")
                if self.show_peak_points.get():
                    abs_max_idx = df['Absorbansi'].idxmax()
                    max_lambda = df['Lambda'].iloc[abs_max_idx]
                    max_abs = df['Absorbansi'].iloc[abs_max_idx]
                    ax.scatter(max_lambda, max_abs, color='black', zorder=1, s=2)
                    ax.text(max_lambda, max_abs, f'{max_abs:.2f}', color='black', fontsize=8, ha='left', va='bottom')
            else:
                ax.plot(df['Lambda'], df['Transmitansi'], label=f"{self.sample_names_var.get().split(',')[i].strip()} (Transmitansi)")

        if self.show_degradasi.get():
            degradasi_text = '\n'.join([f'% Degradasi {self.sample_names_var.get().split(",")[0].strip()} ke {self.sample_names_var.get().split(",")[i+1].strip()} Jam: {self.degradasi_values[i]:.2f}%'
                                       for i in range(len(self.degradasi_values))])
            ax.text(0.05, 0.95, degradasi_text, transform=ax.transAxes,
                    fontsize=8, color='black', ha='left', va='top', bbox=dict(facecolor='white', edgecolor='black', boxstyle='round,pad=0.25'))

        ax.set_xlabel('Panjang Gelombang (nm)')
        ax.set_ylabel('Absorbansi' if show_absorbance else 'Transmitansi')
        ax.set_title(self.graph_title_var.get())

        if self.show_legend.get():
            ax.legend(fontsize=8)

        ax.grid(True)

        self.canvas = FigureCanvasTkAgg(fig, master=self.graph_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack()

        self.toolbar = NavigationToolbar2Tk(self.canvas, self.graph_frame)
        self.toolbar.update()
        self.toolbar.pack()

    def kinetika_degradasi(self):
        if self.data_frames is None:
            messagebox.showerror("Error", "Harap proses data terlebih dahulu!")
            return

        sample_names = self.sample_names_var.get().split(',')
        sample_names = [name.strip() for name in sample_names if name.strip()]

        abs_max_values = [df['Absorbansi'].max() for df in self.data_frames]
        waktu = np.arange(0, len(abs_max_values))

        def model_kinetika(t, k, C0):
            return C0 * np.exp(-k * t)

        try:
            popt, _ = curve_fit(model_kinetika, waktu, abs_max_values, p0=[0.1, abs_max_values[0]])
            k, C0 = popt
        except Exception as e:
            messagebox.showerror("Error", f"Gagal melakukan fitting data: {str(e)}")
            return

        fig, ax = plt.subplots()
        ax.scatter(waktu, abs_max_values, label='Data Eksperimen')
        ax.plot(waktu, model_kinetika(waktu, k, C0), label=f'Fitting: k={k:.4f}, C0={C0:.2f}', color='red')
        ax.set_xlabel('Waktu (jam)')
        ax.set_ylabel('Absorbansi Maksimum')
        ax.set_title('Kinetika Degradasi')
        ax.legend()
        ax.grid(True)

        # Menambahkan persamaan ke grafik
        persamaan = f"Persamaan Kinetika:\nC(t) = {C0:.2f} * e^(-{k:.4f} * t)"
        ax.text(0.05, 0.95, persamaan, transform=ax.transAxes, fontsize=10, color='blue',
                ha='left', va='top', bbox=dict(facecolor='white', edgecolor='black', boxstyle='round,pad=0.5'))

        if self.canvas:
            self.canvas.get_tk_widget().pack_forget()
        if self.toolbar:
            self.toolbar.pack_forget()

        self.canvas = FigureCanvasTkAgg(fig, master=self.graph_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack()

        self.toolbar = NavigationToolbar2Tk(self.canvas, self.graph_frame)
        self.toolbar.update()
        self.toolbar.pack()

    def konsentrasi_relatif(self):
        if self.data_frames is None:
            messagebox.showerror("Error", "Harap proses data terlebih dahulu!")
            return

        sample_names = self.sample_names_var.get().split(',')
        sample_names = [name.strip() for name in sample_names if name.strip()]

        abs_max_values = [df['Absorbansi'].max() for df in self.data_frames]
        C0 = abs_max_values[0]
        konsentrasi_rel = [abs_value / C0 for abs_value in abs_max_values]

        fig, ax = plt.subplots()
        ax.plot(range(len(konsentrasi_rel)), konsentrasi_rel, marker='o', label='Konsentrasi Relatif')
        ax.set_xlabel('Waktu (jam)')
        ax.set_ylabel('Konsentrasi Relatif')
        ax.set_title('Konsentrasi Relatif')
        ax.legend()
        ax.grid(True)

        # Menambahkan persamaan ke grafik
        persamaan = "Persamaan Konsentrasi Relatif:\nC(t)/C₀"
        ax.text(0.05, 0.95, persamaan, transform=ax.transAxes, fontsize=10, color='blue',
                ha='left', va='top', bbox=dict(facecolor='white', edgecolor='black', boxstyle='round,pad=0.5'))

        if self.canvas:
            self.canvas.get_tk_widget().pack_forget()
        if self.toolbar:
            self.toolbar.pack_forget()

        self.canvas = FigureCanvasTkAgg(fig, master=self.graph_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack()

        self.toolbar = NavigationToolbar2Tk(self.canvas, self.graph_frame)
        self.toolbar.update()
        self.toolbar.pack()


if __name__ == "__main__":
    root = Tk()
    app = UVVisAnalyzer(root)
    root.mainloop()