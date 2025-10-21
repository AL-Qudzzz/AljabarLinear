from flask import Flask, render_template, request, jsonify
import numpy as np
import sympy as sp
from sympy import Matrix, Rational

app = Flask(__name__)

# Fungsi untuk formatasi matriks
def format_matrix(matrix):
    """Format matrix for display in proper matrix notation"""
    if isinstance(matrix, (sp.Matrix, list)):
        if isinstance(matrix, list):
            matrix = sp.Matrix(matrix)
        #utk get dimensi matriks nya bris&kolms
        rows = matrix.shape[0]
        cols = matrix.shape[1]
        result = []
        
        # lebar maksimum yg dibutuhin utk setiap kolom
        col_widths = [max(len(str(matrix[i, j])) for i in range(rows)) for j in range(cols)]
        
        # format setiap baris
        for i in range(rows):
            row = []
            for j in range(cols):
                element = str(matrix[i, j])
                # Rata kanan setiap elemen sesuai lebar kolom
                row.append(element.rjust(col_widths[j]))
            result.append("  ".join(row))
            
        # untuk tanda kurung matriks
        max_line_length = len(result[0])
        bracket_height = len(result)
        
        formatted = "⎡" + " " * max_line_length + "⎤\n"
        for idx, line in enumerate(result):
            if idx == 0:
                formatted += "⎢" + line + "⎥\n"
            elif idx == bracket_height - 1:
                formatted += "⎢" + line + "⎥\n"
            else:
                formatted += "⎢" + line + "⎥\n"
        formatted += "⎣" + " " * max_line_length + "⎦"
        
        return formatted
    return str(matrix)

#---------------------------------------------------------------------------------------------------
# Logika untuk operasi matriks gauss-jordan
def gauss_jordan_steps(matrix):
    """
    Perform Gauss-Jordan elimination with step tracking
    """
    A = Matrix(matrix)
    steps = [("Matriks Awal:", A.copy())]
    m, n = A.shape
    r = 0  # baris saat ini
    c = 0  # kolom saat ini
    
    # Proses eliminasi Gauss-Jordan
    while r < m and c < n:
        # langkah 1: Cari pivot non-zero
        pivot = -1
        for i in range(r, m):
            if A[i, c] != 0:
                pivot = i
                break

        # Jika tidak ada pivot di kolom ini, pindah ke kolom berikutnya        
        if pivot == -1:
            c += 1
            continue
            
        # Langkah 2 : Tukar baris jika perlu
        if pivot != r:
            A.row_swap(r, pivot)
            steps.append((f"Tukar baris {r+1} dan {pivot+1}:", A.copy()))
        
        # Langkah 3: Membuat pivot = 1
        pivot_val = A[r, c]
        if pivot_val != 1:
            A.row_op(r, lambda x, k: x/pivot_val)
            steps.append((f"R{r+1} = R{r+1}/{pivot_val}:", A.copy()))
        
        # Langkah 4: Eliminasi elemen diatas dan bawah pivot
        for i in range(m):
            if i != r and A[i, c] != 0:
                factor = A[i, c]
                A.row_op(i, lambda x, k: x - factor*A[r, k])
                steps.append((f"R{i+1} = R{i+1} - {factor}*R{r+1}:", A.copy()))
        
        # Pindah ke kolom berikutnya
        r += 1
        c += 1
    
    return steps

#---------------------------------------------------------------------------------------------------
# Logika untuk kalkulasi RREF dan analisis solusi
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/calculate', methods=['POST'])
def calculate():
    try:
        # Ambil data dari permintaan POST
        data = request.get_json()
        matrix = data['matrix']
        operation = data['operation']
        
        # Konversi ke Matrix SymPy
        A = Matrix(matrix)
        
        result = {
            'status': 'success',
            'steps': [],
            'final_matrix': '',
            'explanation': ''
        }
        
        # Operasi Gauss-Jordan tereduksi
        if operation == 'rref':
            rref_matrix, pivots = A.rref()
            steps = gauss_jordan_steps(matrix)
            result['steps'] = [(step[0], format_matrix(step[1])) for step in steps]
            result['final_matrix'] = format_matrix(rref_matrix)
            
            # Analisis solusi sistem persamaan linear
            m, n = A.shape
            rank = len(pivots)  # Rank = jumlah pivot = jumlah persamaan independen
            num_vars = n - 1  # Kolom terakhir adalah kolom hasil
            
            # Cek konsistensi sistem dengan lebih teliti
            is_consistent = True
            inconsistent_row = -1
            for i in range(m):
                # Cek apakah baris ini adalah baris nol di bagian koefisien
                is_zero_row = True
                for j in range(num_vars):
                    if abs(rref_matrix[i, j]) > 1e-10:
                        is_zero_row = False
                        break
                
                # Jika baris nol tapi konstanta tidak nol, sistem tidak konsisten
                if is_zero_row and abs(rref_matrix[i, -1]) > 1e-10:
                    is_consistent = False
                    inconsistent_row = i
                    break
            
            # Jika sistem tidak konsisten, langsung return
            if not is_consistent:
                konstanta = rref_matrix[inconsistent_row, -1]
                result['explanation'] = f"Tidak ada solusi. Sistem tidak konsisten karena terdapat persamaan: " + \
                                     f"0 = {konstanta} (pada baris {inconsistent_row + 1})."
                return jsonify(result)
            
            # Hitung rank efektif dari matriks augmented dan matriks koefisien
            rank_augmented = 0
            rank_coef = 0
            for i in range(m):
                # Cek rank matriks augmented
                has_nonzero = False
                for j in range(n):
                    if abs(rref_matrix[i, j]) > 1e-10:
                        has_nonzero = True
                        break
                if has_nonzero:
                    rank_augmented += 1
                
                # Cek rank matriks koefisien
                has_nonzero = False
                for j in range(num_vars):
                    if abs(rref_matrix[i, j]) > 1e-10:
                        has_nonzero = True
                        break
                if has_nonzero:
                    rank_coef += 1
            
            # Analisis tipe solusi berdasarkan rank
            if rank_augmented > rank_coef:
                # Jika rank matriks augmented lebih besar dari rank matriks koefisien,
                # berarti ada inkonsistensi
                result['explanation'] = "Tidak ada solusi. Sistem tidak konsisten karena rank matriks augmented " + \
                                     f"({rank_augmented}) lebih besar dari rank matriks koefisien ({rank_coef})."
            elif rank_coef < num_vars:
                # Jika rank matriks koefisien kurang dari jumlah variabel,
                # maka ada solusi tak hingga banyak
                free_vars = [i for i in range(num_vars) if i not in pivots]
                free_vars_str = ", ".join(f"x_{i+1}" for i in free_vars)
                num_free_vars = num_vars - rank_coef
                
                if num_free_vars == 1:
                    result['explanation'] = f"Solusi tak hingga banyak dengan 1 variabel bebas: {free_vars_str}. " + \
                                         "Solusi membentuk garis dalam ruang dimensi yang sesuai."
                elif num_free_vars == 2:
                    result['explanation'] = f"Solusi tak hingga banyak dengan 2 variabel bebas: {free_vars_str}. " + \
                                         "Solusi membentuk bidang dalam ruang dimensi yang sesuai."
                else:
                    result['explanation'] = f"Solusi tak hingga banyak dengan {num_free_vars} variabel bebas: {free_vars_str}. " + \
                                         f"Solusi membentuk ruang dimensi {num_free_vars}."
            else:
                # Jika rank sama dengan jumlah variabel dan sistem konsisten,
                # maka ada solusi unik
                solution_values = []
                for i in range(num_vars):
                    if i in pivots:
                        value = rref_matrix[pivots.index(i), -1]
                        solution_values.append(f"x_{i+1} = {value}")
                        
                solution_str = ", ".join(solution_values)
                result['explanation'] = f"Solusi unik (tunggal) ditemukan: {solution_str}"
            
        # Eliminasi Gauss (OBE) - Bentuk segitiga atas
        elif operation == 'ref':
            ref_steps = []
            current = A.copy()
            m, n = A.shape
            
            for i in range(min(m, n)):
                # Cari pivot selain nol
                pivot_found = False
                for j in range(i, m):
                    if current[j, i] != 0:
                        if j != i:
                            current.row_swap(i, j)
                            ref_steps.append((f"Tukar baris {i+1} dan {j+1}:", current.copy()))
                        pivot_found = True
                        break
                
                if not pivot_found:
                    continue
                    
                # Eliminasi di bawah pivot (tanpa membuat pivot = 1)
                for j in range(i + 1, m):
                    if current[j, i] != 0:
                        factor = current[j, i] / current[i, i]
                        current.row_op(j, lambda x, k: x - factor*current[i, k])
                        ref_steps.append((f"R{j+1} = R{j+1} - {factor}*R{i+1}:", current.copy()))
            
            result['steps'] = [(step[0], format_matrix(step[1])) for step in ref_steps]
            result['final_matrix'] = format_matrix(current)
            result['explanation'] = "Hasil Eliminasi Gauss (OBE) - Bentuk segitiga atas diperoleh."
            
        # Eliminasi Gauss dengan Satu Utama
        elif operation == 'ref-leading-one':
            ref_steps = []
            current = A.copy()
            m, n = A.shape
            
            for i in range(min(m, n)):
                # Cari pivot selain nol
                pivot_found = False
                for j in range(i, m):
                    if current[j, i] != 0:
                        if j != i:
                            current.row_swap(i, j)
                            ref_steps.append((f"Tukar baris {i+1} dan {j+1}:", current.copy()))
                        pivot_found = True
                        break
                
                if not pivot_found:
                    continue
                
                # Buat pivot menjadi 1
                pivot_val = current[i, i]
                if pivot_val != 1:
                    current.row_op(i, lambda x, k: x/pivot_val)
                    ref_steps.append((f"R{i+1} = R{i+1}/{pivot_val} (Membuat pivot = 1):", current.copy()))
                    
                # Eliminasi di bawah pivot
                for j in range(i + 1, m):
                    if current[j, i] != 0:
                        factor = current[j, i]
                        current.row_op(j, lambda x, k: x - factor*current[i, k])
                        ref_steps.append((f"R{j+1} = R{j+1} - {factor}*R{i+1}:", current.copy()))
            
            result['steps'] = [(step[0], format_matrix(step[1])) for step in ref_steps]
            result['final_matrix'] = format_matrix(current)
            result['explanation'] = "Hasil Eliminasi Gauss dengan Satu Utama - Bentuk segitiga atas dengan leading 1 diperoleh."
            
        # Eliminasi Gauss-Jordan (Tereduksi)
        elif operation == 'gauss-jordan':
            steps = gauss_jordan_steps(matrix)
            result['steps'] = [(step[0], format_matrix(step[1])) for step in steps]
            result['final_matrix'] = format_matrix(steps[-1][1])
            result['explanation'] = "Hasil Eliminasi Gauss-Jordan (Bentuk Tereduksi) diperoleh."

        # Kirim hasil sebagai JSON    
        return jsonify(result)

    # menangani kesalahan jika terjadi error pas proses
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        })

# untuk menjalankan aplikasi flask nya
if __name__ == '__main__':
    app.run(debug=True)