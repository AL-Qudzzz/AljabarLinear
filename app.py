from flask import Flask, render_template, request, jsonify
import numpy as np
import sympy as sp
from sympy import Matrix, Rational

app = Flask(__name__)

def format_matrix(matrix):
    """Format matrix for display in proper matrix notation"""
    if isinstance(matrix, (sp.Matrix, list)):
        if isinstance(matrix, list):
            matrix = sp.Matrix(matrix)
        rows = matrix.shape[0]
        cols = matrix.shape[1]
        result = []
        
        # Maximum width needed for each column
        col_widths = [max(len(str(matrix[i, j])) for i in range(rows)) for j in range(cols)]
        
        for i in range(rows):
            row = []
            for j in range(cols):
                element = str(matrix[i, j])
                # Pad the element to match column width
                row.append(element.rjust(col_widths[j]))
            result.append("  ".join(row))
            
        # Add matrix brackets
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

def gauss_jordan_steps(matrix):
    """
    Perform Gauss-Jordan elimination with step tracking
    """
    A = Matrix(matrix)
    steps = [("Matriks Awal:", A.copy())]
    m, n = A.shape
    r = 0  # baris saat ini
    c = 0  # kolom saat ini
    
    while r < m and c < n:
        # Cari pivot non-zero
        pivot = -1
        for i in range(r, m):
            if A[i, c] != 0:
                pivot = i
                break
                
        if pivot == -1:
            c += 1
            continue
            
        # Tukar baris jika perlu
        if pivot != r:
            A.row_swap(r, pivot)
            steps.append((f"Tukar baris {r+1} dan {pivot+1}:", A.copy()))
        
        # Buat pivot menjadi 1
        pivot_val = A[r, c]
        if pivot_val != 1:
            A.row_op(r, lambda x, k: x/pivot_val)
            steps.append((f"R{r+1} = R{r+1}/{pivot_val}:", A.copy()))
        
        # Eliminasi kolom
        for i in range(m):
            if i != r and A[i, c] != 0:
                factor = A[i, c]
                A.row_op(i, lambda x, k: x - factor*A[r, k])
                steps.append((f"R{i+1} = R{i+1} - {factor}*R{r+1}:", A.copy()))
        
        r += 1
        c += 1
    
    return steps

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/calculate', methods=['POST'])
def calculate():
    try:
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
        
        if operation == 'rref':
            rref_matrix, pivots = A.rref()
            steps = gauss_jordan_steps(matrix)
            result['steps'] = [(step[0], format_matrix(step[1])) for step in steps]
            result['final_matrix'] = format_matrix(rref_matrix)
            result['explanation'] = "Bentuk eselon baris tereduksi (RREF) diperoleh."
            
        elif operation == 'ref':
            # Eliminasi Gauss untuk REF
            ref_steps = []
            current = A.copy()
            m, n = A.shape
            
            for i in range(min(m, n)):
                # Cari pivot non-zero
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
                    
                # Eliminasi di bawah pivot
                for j in range(i + 1, m):
                    if current[j, i] != 0:
                        factor = current[j, i] / current[i, i]
                        current.row_op(j, lambda x, k: x - factor*current[i, k])
                        ref_steps.append((f"R{j+1} = R{j+1} - {factor}*R{i+1}:", current.copy()))
            
            result['steps'] = [(step[0], format_matrix(step[1])) for step in ref_steps]
            result['final_matrix'] = format_matrix(current)
            result['explanation'] = "Bentuk eselon baris (REF) diperoleh."
            
        elif operation == 'gauss-jordan':
            steps = gauss_jordan_steps(matrix)
            result['steps'] = [(step[0], format_matrix(step[1])) for step in steps]
            result['final_matrix'] = format_matrix(steps[-1][1])
            result['explanation'] = "Eliminasi Gauss-Jordan selesai."
            
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        })

if __name__ == '__main__':
    app.run(debug=True)