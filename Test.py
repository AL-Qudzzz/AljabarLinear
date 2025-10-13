import tkinter as tk
from tkinter import messagebox, ttk
import numpy as np

# --- FUNGSI LOGIKA PERHITUNGAN MATRIKS ---

def ke_bentuk_eselon_baris(matrix):
    # Gunakan dtype=np.float64 untuk efisiensi
    mat = np.copy(matrix).astype(np.float64)
    num_rows, num_cols = mat.shape
    pivot_row = 0
    langkah_langkah = [("Matriks Awal:", mat.copy())]

    for j in range(num_cols):
        if pivot_row >= num_rows:
            break

        # Cari baris dengan nilai absolut maksimum di kolom j (pivoting)
        # untuk stabilitas numerik.
        i = pivot_row
        max_row = i
        while i < num_rows:
            if abs(mat[i, j]) > abs(mat[max_row, j]):
                max_row = i
            i += 1

        # Tukar baris pivot saat ini dengan baris yang memiliki nilai maksimum
        if max_row != pivot_row:
            mat[[pivot_row, max_row]] = mat[[max_row, pivot_row]]
            langkah_langkah.append((f"Tukar Baris {pivot_row+1} dan {max_row+1}", np.copy(mat)))

        # Jika elemen pivot adalah nol, lewati kolom ini
        if abs(mat[pivot_row, j]) < 1e-10:
            continue

        # Buat elemen di bawah pivot menjadi nol
        for i in range(pivot_row + 1, num_rows):
            faktor = mat[i, j] / mat[pivot_row, j]
            if faktor != 0:
                mat[i] = mat[i] - faktor * mat[pivot_row]
                langkah_langkah.append((f"R{i+1} = R{i+1} - ({faktor:.2f})*R{pivot_row+1}", np.copy(mat)))

        pivot_row += 1

    # Atasi nilai yang sangat kecil mendekati nol
    mat[np.abs(mat) < 1e-10] = 0
    langkah_langkah.append(("Hasil Akhir (Bentuk Eselon Baris):", np.copy(mat)))
    return mat, langkah_langkah

def ke_bentuk_eselon_baris_tereduksi(matrix):
    """
    Mengubah matriks menjadi bentuk eselon baris tereduksi.
    """
    # Pertama, ubah ke bentuk eselon baris biasa
    mat_eselon, langkah_eselon = ke_bentuk_eselon_baris(matrix)
    mat = np.copy(mat_eselon).astype(float)
    num_rows, num_cols = mat.shape

    langkah_langkah = langkah_eselon[:-1] # Hapus langkah terakhir dari eselon
    langkah_langkah.append(("Lanjut ke Bentuk Tereduksi:", np.copy(mat)))

    for i in range(num_rows - 1, -1, -1):
        # Cari pivot (elemen non-nol pertama dari kiri)
        pivot_col = -1
        for j in range(num_cols):
            if abs(mat[i, j]) > 1e-10:
                pivot_col = j
                break

        if pivot_col == -1:
            continue # Baris ini adalah baris nol

        # Jadikan pivot sebagai 1 (Satu Utama)
        pivot_val = mat[i, pivot_col]
        if abs(pivot_val - 1.0) > 1e-10:
            mat[i] = mat[i] / pivot_val
            langkah_langkah.append((f"R{i+1} = R{i+1} / {pivot_val:.2f}", np.copy(mat)))

        # Buat elemen di ATAS pivot menjadi nol
        for k in range(i - 1, -1, -1):
            faktor = mat[k, pivot_col]
            if faktor != 0:
                mat[k] = mat[k] - faktor * mat[i]
                langkah_langkah.append((f"R{k+1} = R{k+1} - ({faktor:.2f})*R{i+1}", np.copy(mat)))

    mat[np.abs(mat) < 1e-10] = 0
    langkah_langkah.append(("Hasil Akhir (Bentuk Eselon Baris Tereduksi):", np.copy(mat)))
    return mat, langkah_langkah

def analisis_solusi(matrix):
    """
    Menganalisis jenis solusi dari matriks augmented
    yang sudah dalam bentuk eselon baris tereduksi.
    """
    rref_matrix, _ = ke_bentuk_eselon_baris_tereduksi(matrix)
    num_rows, num_cols = rref_matrix.shape
    num_vars = num_cols - 1

    # Cek inkonsistensi (baris [0 0 ... | c] dengan c != 0)
    for i in range(num_rows):
        row = rref_matrix[i, :]
        koefisien_nol = np.all(np.abs(row[:num_vars]) < 1e-10)
        konstanta_non_nol = abs(row[num_vars]) > 1e-10
        if koefisien_nol and konstanta_non_nol:
            return f"Tidak Ada Solusi.\nTerjadi inkonsistensi pada baris {i+1} (0 = {row[num_vars]:.2f})."

    # Hitung rank (jumlah baris non-nol atau jumlah satu utama)
    rank = 0
    for i in range(num_rows):
        if not np.all(np.abs(rref_matrix[i, :]) < 1e-10):
            rank += 1

    if rank < num_vars:
        return f"Solusi Tak Hingga Banyak.\nJumlah variabel ({num_vars}) > Rank matriks ({rank})."
    else: # rank == num_vars
        solusi = []
        for i in range(rank):
            # Cari kolom pivot untuk baris ini
            pivot_col = np.where(np.abs(rref_matrix[i, :num_vars]) > 1e-10)[0][0]
            nilai_solusi = rref_matrix[i, num_vars]
            solusi.append(f"x{pivot_col+1} = {nilai_solusi:.2f}")

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
        button_frame.columnconfigure((0, 1, 2), weight=1)

        ttk.Button(button_frame, text="Bentuk Eselon Baris", command=self.hitung_eselon).grid(row=0, column=0, padx=5, sticky="ew")
        ttk.Button(button_frame, text="Bentuk Tereduksi", command=self.hitung_tereduksi).grid(row=0, column=1, padx=5, sticky="ew")
        ttk.Button(button_frame, text="Analisis Solusi", command=self.tentukan_solusi).grid(row=0, column=2, padx=5, sticky="ew")

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
            hasil, langkah = ke_bentuk_eselon_baris(matrix)
            self.tampilkan_hasil("Hasil - Bentuk Eselon Baris", langkah)

    def hitung_tereduksi(self):
        matrix = self.get_matrix_from_input()
        if matrix is not None:
            hasil, langkah = ke_bentuk_eselon_baris_tereduksi(matrix)
            self.tampilkan_hasil("Hasil - Bentuk Eselon Baris Tereduksi", langkah)

    def tentukan_solusi(self):
        matrix = self.get_matrix_from_input()
        if matrix is not None:
            if matrix.shape[1] <= 1:
                messagebox.showerror("Error", "Analisis solusi memerlukan matriks augmented (minimal 2 kolom).")
                return

            _, langkah_rref = ke_bentuk_eselon_baris_tereduksi(matrix)
            solusi_text = analisis_solusi(matrix)

            # Gabungkan langkah-langkah RREF dengan hasil analisis
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
