import tkinter as tk
from tkinter import messagebox, ttk
import numpy as np

# --- FUNGSI LOGIKA PERHITUNGAN MATRIKS ---

def eliminasi_gauss(matrix, make_one=False, jordan=False):
    """
    Fungsi umum untuk semua jenis eliminasi Gauss
    make_one: True untuk Satu Utama, False untuk OBE biasa
    jordan: True untuk Gauss-Jordan, False untuk Gauss biasa
    """
    mat = np.copy(matrix).astype(np.float64)
    num_rows, num_cols = mat.shape
    pivot_row = 0
    langkah_langkah = [("Matriks Awal:", mat.copy())]

    # Forward elimination
    for j in range(num_cols):
        if pivot_row >= num_rows:
            break

        # Cari pivot terbesar (partial pivoting)
        max_row = max(range(pivot_row, num_rows), 
                     key=lambda i: abs(mat[i, j]))
        
        if abs(mat[max_row, j]) < 1e-10:
            continue

        # Tukar baris jika perlu
        if max_row != pivot_row:
            mat[[pivot_row, max_row]] = mat[[max_row, pivot_row]]
            langkah_langkah.append((f"Tukar baris {pivot_row+1} dan {max_row+1}:", mat.copy()))

        # Buat pivot menjadi 1 jika diminta
        if make_one:
            pivot_val = mat[pivot_row, j]
            if abs(pivot_val - 1.0) > 1e-10:
                mat[pivot_row] = mat[pivot_row] / pivot_val
                langkah_langkah.append((f"R{pivot_row+1} = R{pivot_row+1}/{pivot_val:.2f}:", mat.copy()))

        # Eliminasi di bawah pivot
        rows_to_eliminate = range(num_rows) if jordan else range(pivot_row + 1, num_rows)
        for i in rows_to_eliminate:
            if i != pivot_row and abs(mat[i, j]) > 1e-10:
                faktor = mat[i, j] / mat[pivot_row, j]
                mat[i] = mat[i] - faktor * mat[pivot_row]
                langkah_langkah.append((f"R{i+1} = R{i+1} - ({faktor:.2f})*R{pivot_row+1}:", mat.copy()))

        pivot_row += 1

    # Atasi nilai yang sangat kecil mendekati nol
    mat[np.abs(mat) < 1e-10] = 0
    
    # Tentukan judul hasil akhir berdasarkan jenis eliminasi
    if jordan:
        hasil = "Hasil Akhir (Eliminasi Gauss-Jordan):"
    elif make_one:
        hasil = "Hasil Akhir (Eliminasi Gauss dengan Satu Utama):"
    else:
        hasil = "Hasil Akhir (Eliminasi Gauss/OBE):"
    langkah_langkah.append((hasil, mat.copy()))
    
    return mat, langkah_langkah

def analisis_solusi(matrix):
    """
    Menganalisis jenis solusi dari matriks augmented
    """
    # Dapatkan bentuk tereduksi
    rref_matrix, _ = eliminasi_gauss(matrix, make_one=True, jordan=True)
    num_rows, num_cols = rref_matrix.shape
    num_vars = num_cols - 1

    # Cek inkonsistensi
    for i in range(num_rows):
        row = rref_matrix[i, :]
        if np.all(np.abs(row[:num_vars]) < 1e-10) and abs(row[-1]) > 1e-10:
            return f"Tidak Ada Solusi.\nTerjadi inkonsistensi pada baris {i+1} (0 = {row[-1]:.2f})."

    # Hitung rank efektif
    rank = sum(1 for i in range(num_rows) 
              if not np.all(np.abs(rref_matrix[i, :]) < 1e-10))

    # Analisis tipe solusi
    if rank < num_vars:
        return f"Solusi Tak Hingga Banyak.\nJumlah variabel ({num_vars}) > Rank matriks ({rank})."
    
    # Jika sampai di sini, solusi unik
    solusi = []
    for i in range(rank):
        pivot_col = next((j for j in range(num_vars) 
                         if abs(rref_matrix[i, j]) > 1e-10), -1)
        if pivot_col != -1:
            solusi.append(f"x{pivot_col+1} = {rref_matrix[i, -1]:.2f}")

    return "Solusi Unik (Tunggal).\n" + "\n".join(solusi)


# --- KELAS UNTUK ANTARMUKA PENGGUNA (GUI) ---

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Kalkulator Matriks OBE")
        self.geometry("400x200")

        self.entries = []
        self.rows = 0
        self.cols = 0

        self.create_widgets_ukuran()

    def clear_frame(self):
        for widget in self.winfo_children():
            widget.destroy()

    def create_widgets_ukuran(self):
        self.clear_frame()
        self.geometry("400x200")
        frame = ttk.Frame(self, padding="10")
        frame.pack(expand=True, fill="both")

        ttk.Label(frame, text="Masukkan Ukuran Matriks (termasuk kolom konstanta):").pack(pady=5)

        # Frame untuk input ukuran
        size_frame = ttk.Frame(frame)
        size_frame.pack(pady=10)

        ttk.Label(size_frame, text="Jumlah Baris:").grid(row=0, column=0, padx=5, sticky="e")
        self.row_entry = ttk.Entry(size_frame, width=5)
        self.row_entry.grid(row=0, column=1, padx=5)

        ttk.Label(size_frame, text="Jumlah Kolom:").grid(row=1, column=0, padx=5, sticky="e")
        self.col_entry = ttk.Entry(size_frame, width=5)
        self.col_entry.grid(row=1, column=1, padx=5)

        ttk.Button(frame, text="Buat Matriks", command=self.create_widgets_matriks).pack(pady=10)

    def create_widgets_matriks(self):
        try:
            self.rows = int(self.row_entry.get())
            self.cols = int(self.col_entry.get())
            if self.rows <= 0 or self.cols <= 1:
                raise ValueError("Ukuran tidak valid.")
        except ValueError:
            messagebox.showerror("Error", "Masukkan jumlah baris dan kolom yang valid (bilangan bulat positif).")
            return

        self.clear_frame()

        # Sesuaikan ukuran window dengan batas maksimum
        max_width = min(800, max(450, self.cols * 60))
        max_height = min(600, max(300, self.rows * 40 + 150))
        self.geometry(f"{max_width}x{max_height}")

        # Buat main frame dengan scrollbar
        container = ttk.Frame(self)
        container.pack(expand=True, fill="both")
        
        # Tambahkan canvas dan scrollbar
        canvas = tk.Canvas(container)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        
        main_frame = ttk.Frame(canvas, padding="10")
        main_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        
        canvas.create_window((0, 0), window=main_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Pack scrollbar dan canvas
        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", expand=True, fill="both")

        ttk.Label(main_frame, text="Masukkan Elemen Matriks:").pack(pady=(0, 10))

        # Frame untuk grid entry matriks dengan konfigurasi grid
        matrix_frame = ttk.Frame(main_frame)
        matrix_frame.pack(pady=5)
        self.entries = []
        for i in range(self.rows):
            row_entries = []
            for j in range(self.cols):
                # Tambahkan garis pemisah untuk kolom konstanta
                if j == self.cols - 1:
                    ttk.Label(matrix_frame, text="|").grid(row=i, column=j*2, padx=5)

                entry = ttk.Entry(matrix_frame, width=5)
                entry.grid(row=i, column=j*2 + (1 if j == self.cols - 1 else 0), padx=5, pady=5)
                row_entries.append(entry)
            self.entries.append(row_entries)

        # Frame untuk tombol aksi
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=20, fill="x", expand=True)
        button_frame.columnconfigure((0, 1), weight=1)  # Dua kolom dengan bobot sama

        # Tombol baris pertama
        ttk.Button(button_frame, text="1. Eliminasi Gauss (OBE)", 
                  command=self.hitung_eselon).grid(row=0, column=0, padx=5, pady=2, sticky="ew")
        ttk.Button(button_frame, text="2. Eliminasi Gauss (Satu Utama)", 
                  command=self.hitung_tereduksi).grid(row=0, column=1, padx=5, pady=2, sticky="ew")
        
        # Tombol baris kedua
        ttk.Button(button_frame, text="3. Eliminasi Gauss-Jordan", 
                  command=self.gauss_jordan).grid(row=1, column=0, padx=5, pady=2, sticky="ew")
        ttk.Button(button_frame, text="4. Analisis Solusi", 
                  command=self.tentukan_solusi).grid(row=1, column=1, padx=5, pady=2, sticky="ew")

        ttk.Button(main_frame, text="< Kembali (Ubah Ukuran)", command=self.create_widgets_ukuran).pack(pady=10)

    def get_matrix_from_input(self):
        matrix = []
        try:
            for i in range(self.rows):
                row = [float(self.entries[i][j].get()) for j in range(self.cols)]
                matrix.append(row)
            return np.array(matrix)
        except (ValueError, IndexError):
            messagebox.showerror("Error", "Pastikan semua input adalah angka dan tidak ada yang kosong.")
            return None

    def format_matrix(self, matrix):
        s = ""
        for row in matrix:
            s += "  ".join([f"{item:8.2f}".rstrip('0').rstrip('.') for item in row]) + "\n"
        return s.strip()

    def tampilkan_hasil(self, title, steps):
        hasil_window = tk.Toplevel(self)
        hasil_window.title(title)

        text_widget = tk.Text(hasil_window, wrap="word", font=("Courier New", 10), height=25, width=80)
        text_widget.pack(padx=10, pady=10, fill="both", expand=True)

        for deskripsi, matriks in steps:
            text_widget.insert(tk.END, f"{deskripsi}\n", "bold")
            text_widget.insert(tk.END, self.format_matrix(matriks) + "\n\n")

        text_widget.tag_configure("bold", font=("Courier New", 10, "bold"))
        text_widget.config(state="disabled") # Buat read-only

    def hitung_eselon(self):
        matrix = self.get_matrix_from_input()
        if matrix is not None:
            # Eliminasi Gauss (OBE)
            hasil, langkah = eliminasi_gauss(matrix, make_one=False, jordan=False)
            self.tampilkan_hasil("Hasil - Eliminasi Gauss (OBE)", langkah)

    def hitung_tereduksi(self):
        matrix = self.get_matrix_from_input()
        if matrix is not None:
            # Eliminasi Gauss dengan Satu Utama
            hasil, langkah = eliminasi_gauss(matrix, make_one=True, jordan=False)
            self.tampilkan_hasil("Hasil - Eliminasi Gauss (Satu Utama)", langkah)

    def gauss_jordan(self):
        matrix = self.get_matrix_from_input()
        if matrix is not None:
            # Eliminasi Gauss-Jordan
            hasil, langkah = eliminasi_gauss(matrix, make_one=True, jordan=True)
            self.tampilkan_hasil("Hasil - Eliminasi Gauss-Jordan", langkah)

    def tentukan_solusi(self):
        matrix = self.get_matrix_from_input()
        if matrix is not None:
            if matrix.shape[1] <= 1:
                messagebox.showerror("Error", "Analisis solusi memerlukan matriks augmented (minimal 2 kolom).")
                return

            # Dapatkan langkah-langkah Gauss-Jordan dan analisis solusi
            rref_matrix, langkah_rref = eliminasi_gauss(matrix, make_one=True, jordan=True)
            solusi_text = analisis_solusi(matrix)
            langkah_analisis = langkah_rref + [("Analisis Solusi:", solusi_text)]
            self.tampilkan_hasil_solusi("Hasil - Analisis Solusi", langkah_analisis)

    def tampilkan_hasil_solusi(self, title, steps):
        hasil_window = tk.Toplevel(self)
        hasil_window.title(title)

        text_widget = tk.Text(hasil_window, wrap="word", font=("Courier New", 10), height=25, width=80)
        text_widget.pack(padx=10, pady=10, fill="both", expand=True)

        for deskripsi, konten in steps:
            text_widget.insert(tk.END, f"{deskripsi}\n", "bold")
            if isinstance(konten, np.ndarray):
                text_widget.insert(tk.END, self.format_matrix(konten) + "\n\n")
            else: # String untuk hasil analisis
                text_widget.insert(tk.END, konten + "\n\n", "result")

        text_widget.tag_configure("bold", font=("Courier New", 10, "bold"))
        text_widget.tag_configure("result", font=("Courier New", 10, "italic"))
        text_widget.config(state="disabled")


if __name__ == "__main__":
    app = App()
    app.mainloop()
