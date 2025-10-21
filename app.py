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
            num_vars = n - 1  # Kolom terakhir adalah kolom hasil

            # Cek inkonsistensi menggunakan metode yang sama dengan Test.py
            for i in range(m):
                row = rref_matrix.row(i)
                # Cek apakah semua koefisien adalah nol (kecuali kolom terakhir)
                koefisien_nol = all(abs(row[j]) < 1e-10 for j in range(num_vars))
                # Cek apakah konstanta tidak nol
                konstanta_non_nol = abs(row[num_vars]) > 1e-10
                
                if koefisien_nol and konstanta_non_nol:
                    result['explanation'] = f"Tidak ada solusi.\nTerjadi inkonsistensi pada baris {i+1} " + \
                                         f"(0 = {row[num_vars]})."
                    return jsonify(result)

            # Hitung rank efektif (jumlah baris non-nol)
            rank = 0
            for i in range(m):
                if not all(abs(rref_matrix[i, j]) < 1e-10 for j in range(n)):
                    rank += 1

            # Analisis tipe solusi berdasarkan rank
            if rank < num_vars:
                # Hitung variabel bebas
                pivot_cols = []
                for i in range(m):
                    for j in range(num_vars):
                        if abs(rref_matrix[i, j]) > 1e-10:
                            pivot_cols.append(j)
                            break
                
                free_vars = [i+1 for i in range(num_vars) if i not in pivot_cols]
                free_vars_str = ", ".join(f"x_{i}" for i in free_vars)
                result['explanation'] = f"Solusi tak hingga banyak.\nJumlah variabel ({num_vars}) > " + \
                                     f"Rank matriks ({rank}).\nVariabel bebas: {free_vars_str}"
            else:
                # Solusi unik - verifikasi dan dapatkan nilai
                solution_found = True
                solution_values = []
                
                # Pastikan setiap variabel memiliki nilai yang terdefinisi
                for i in range(num_vars):
                    value_found = False
                    for row_idx in range(m):
                        if abs(rref_matrix[row_idx, i]) > 1e-10:
                            # Pastikan ini adalah baris yang mendefinisikan variabel ini
                            is_defining_row = all(abs(rref_matrix[row_idx, j]) < 1e-10 for j in range(i))
                            if is_defining_row:
                                value_found = True
                                solution_values.append(f"x_{i+1} = {rref_matrix[row_idx, -1]}")
                                break
                    
                    if not value_found:
                        solution_found = False
                        break
                
                if solution_found and len(solution_values) == num_vars:
                    result['explanation'] = "Solusi unik (tunggal).\n" + "\n".join(solution_values)
                else:
                    result['explanation'] = "Tidak ada solusi.\nSistem tidak konsisten."
            
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