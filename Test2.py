import tkinter as tk
from tkinter import messagebox, ttk
import sympy

# --- FUNGSI LOGIKA PERHITUNGAN MATRIKS DENGAN SYMPY ---

def solve_matrix_sympy(matrix_input):
    """
    Menghitung Bentuk Eselon Baris Tereduksi (RREF) dan menganalisis solusi
    dari sistem persamaan linear menggunakan SymPy untuk presisi eksak.

    Args:
        matrix_input (list of lists): Matriks augmented.

    Returns:
        tuple: (initial_matrix, rref_matrix, analysis_string)
    """
    try:
        # Konversi ke SymPy Matrix dengan tipe data Rational untuk presisi penuh (pecahan)
        initial_matrix = sympy.Matrix(matrix_input).applyfunc(sympy.Rational)
        
        # Hitung RREF dan kolom pivot. Ini adalah inti dari eliminasi Gauss-Jordan.
        rref_matrix, pivot_columns = initial_matrix.rref()
        
        # --- Analisis Solusi ---
        num_vars = initial_matrix.cols - 1
        rank = len(pivot_columns)
        
        # Cek inkonsistensi (misal: baris [0, 0, ..., 1])
        for r in range(rank, initial_matrix.rows):
            if rref_matrix[r, -1] != 0:
                analysis = f"Tidak Ada Solusi.\nTerjadi inkonsistensi pada baris {r+1} (0 = {rref_matrix[r, -1]})."
                return initial_matrix, rref_matrix, analysis

        # Cek solusi unik vs. tak hingga
        if rank < num_vars:
            # Solusi tak hingga banyak
            free_vars = [i for i in range(num_vars) if i not in pivot_columns]
            analysis = (f"Solusi Tak Hingga Banyak.\n"
                        f"Rank Matriks ({rank}) < Jumlah Variabel ({num_vars}).\n"
                        f"Variabel bebas: " + ", ".join([f"x{v+1}" for v in free_vars]))
        else: # rank == num_vars
            # Solusi unik
            solusi = []
            # Pastikan hanya ada satu solusi, tidak ada baris nol yang aneh
            if rank == initial_matrix.rows or all(rref_matrix[i, -1] == 0 for i in range(rank, initial_matrix.rows)):
                for i, p_col in enumerate(pivot_columns):
                    if p_col < num_vars:
                        solusi.append(f"x{p_col+1} = {rref_matrix[i, -1]}")
                analysis = "Solusi Unik (Tunggal).\n" + "\n".join(solusi)
            else:
                 analysis = "Tidak Ada Solusi.\nMatriks inkonsisten setelah reduksi."

        return initial_matrix, rref_matrix, analysis
        
    except Exception as e:
        return None, None, f"Terjadi error saat kalkulasi: {e}"


# --- KELAS UNTUK ANTARMUKA PENGGUNA (GUI) ---

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Kalkulator Matriks OBE (SymPy)")
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

        max_width = min(800, max(450, self.cols * 60))
        max_height = min(600, max(300, self.rows * 40 + 150))
        self.geometry(f"{max_width}x{max_height}")

        container = ttk.Frame(self)
        container.pack(expand=True, fill="both")
        
        canvas = tk.Canvas(container)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        
        main_frame = ttk.Frame(canvas, padding="10")
        main_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        
        canvas.create_window((0, 0), window=main_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", expand=True, fill="both")

        ttk.Label(main_frame, text="Masukkan Elemen Matriks:").pack(pady=(0, 10))

        matrix_frame = ttk.Frame(main_frame)
        matrix_frame.pack(pady=5)
        self.entries = []
        for i in range(self.rows):
            row_entries = []
            for j in range(self.cols):
                if j == self.cols - 1:
                    ttk.Label(matrix_frame, text="|").grid(row=i, column=j*2, padx=5)

                entry = ttk.Entry(matrix_frame, width=5)
                entry.grid(row=i, column=j*2 + (1 if j == self.cols - 1 else 0), padx=5, pady=5)
                row_entries.append(entry)
            self.entries.append(row_entries)

        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=20, fill="x", expand=True)
        button_frame.columnconfigure(0, weight=1)

        ttk.Button(button_frame, text="Hitung & Analisis Solusi", command=self.run_full_analysis).grid(row=0, column=0, padx=5, sticky="ew")

        ttk.Button(main_frame, text="< Kembali (Ubah Ukuran)", command=self.create_widgets_ukuran).pack(pady=10)

    def get_matrix_from_input(self):
        matrix = []
        try:
            for i in range(self.rows):
                row = [float(self.entries[i][j].get()) for j in range(self.cols)]
                matrix.append(row)
            return matrix
        except (ValueError, IndexError):
            messagebox.showerror("Error", "Pastikan semua input adalah angka dan tidak ada yang kosong.")
            return None

    def run_full_analysis(self):
        matrix = self.get_matrix_from_input()
        if matrix is not None:
            if len(matrix[0]) <= 1:
                messagebox.showerror("Error", "Analisis solusi memerlukan matriks augmented (minimal 2 kolom).")
                return

            initial_mat, rref_mat, analysis_text = solve_matrix_sympy(matrix)

            if initial_mat is None:
                messagebox.showerror("Error Kalkulasi", analysis_text)
                return

            self.show_analysis_results("Hasil Analisis Matriks", initial_mat, rref_mat, analysis_text)

    def show_analysis_results(self, title, initial_matrix, rref_matrix, analysis_text):
        hasil_window = tk.Toplevel(self)
        hasil_window.title(title)
        hasil_window.geometry("600x400")

        text_widget = tk.Text(hasil_window, wrap="none", font=("Courier New", 10))
        x_scrollbar = ttk.Scrollbar(hasil_window, orient="horizontal", command=text_widget.xview)
        y_scrollbar = ttk.Scrollbar(hasil_window, orient="vertical", command=text_widget.yview)
        text_widget.configure(xscrollcommand=x_scrollbar.set, yscrollcommand=y_scrollbar.set)
        
        y_scrollbar.pack(side="right", fill="y")
        x_scrollbar.pack(side="bottom", fill="x")
        text_widget.pack(padx=10, pady=10, fill="both", expand=True)

        text_widget.insert(tk.END, "Matriks Awal:\n", "bold")
        text_widget.insert(tk.END, str(initial_matrix) + "\n\n")

        text_widget.insert(tk.END, "Bentuk Eselon Baris Tereduksi (RREF):\n", "bold")
        text_widget.insert(tk.END, str(rref_matrix) + "\n\n")
        
        text_widget.insert(tk.END, "Analisis Solusi:\n", "bold")
        text_widget.insert(tk.END, analysis_text + "\n", "result")

        text_widget.tag_configure("bold", font=("Courier New", 10, "bold"))
        text_widget.tag_configure("result", font=("Courier New", 10, "italic"))
        text_widget.config(state="disabled")

if __name__ == "__main__":
    app = App()
    app.mainloop()
