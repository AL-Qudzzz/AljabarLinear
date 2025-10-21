# Kalkulator Matriks - Operasi Baris Elementer

Aplikasi kalkulator matriks yang memungkinkan pengguna untuk melakukan operasi baris elementer, termasuk mencari bentuk eselon baris (REF), bentuk eselon baris tereduksi (RREF), dan eliminasi Gauss-Jordan. Aplikasi ini tersedia dalam dua versi: GUI berbasis Tkinter dan Web berbasis Flask.

## Fitur

- Perhitungan bentuk eselon baris (REF)
- Perhitungan bentuk eselon baris tereduksi (RREF)
- Eliminasi Gauss-Jordan
- Analisis solusi sistem persamaan linear
- Tampilan langkah-demi-langkah proses perhitungan
- Dukungan untuk pecahan eksak menggunakan SymPy
- Antarmuka web responsif (versi Flask)
- GUI desktop (versi Tkinter)

## Prasyarat

Sebelum menjalankan aplikasi, pastikan Anda telah menginstal:

- Python 3.8 atau yang lebih baru
- pip (Python package installer)

## Instalasi

1. Clone repositori ini:
```bash
git clone https://github.com/AL-Qudzzz/AljabarLinear.git
cd AljabarLinear
```

2. Buat dan aktifkan virtual environment:
```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# Linux/MacOS
python3 -m venv .venv
source .venv/bin/activate
```

3. Install dependensi yang diperlukan:
```bash
pip install flask numpy sympy
```

## Cara Menjalankan Aplikasi

### Versi Web (Flask)

1. Pastikan Anda berada di direktori project
2. Jalankan server Flask:
```bash
flask run
```
3. Buka browser dan akses `http://localhost:5000`

### Versi Desktop (Tkinter)

1. Jalankan file `Test2.py`:
```bash
python Test2.py
```

## Cara Penggunaan

### Versi Web

1. Masukkan ukuran matriks (jumlah baris dan kolom)
2. Klik "Buat Matriks"
3. Isi elemen-elemen matriks
4. Pilih operasi yang diinginkan:
   - Hitung Bentuk Eselon Baris (REF)
   - Hitung Bentuk Eselon Baris Tereduksi (RREF)
   - Eliminasi Gauss-Jordan
5. Hasil akan ditampilkan dengan langkah-langkah penyelesaian

### Versi Desktop

1. Masukkan ukuran matriks
2. Klik "Buat Matriks"
3. Isi elemen-elemen matriks
4. Klik "Hitung & Analisis Solusi"
5. Hasil akan ditampilkan dalam jendela baru

## Struktur Project

```
AljabarLinear/
│
├── app.py                 # Aplikasi Flask
├── Test2.py              # Aplikasi Tkinter
├── templates/
│   └── index.html        # Template HTML untuk versi web
├── static/               # Assets statis (CSS, JS, dll)
└── README.md            # Dokumentasi
```

## Kontribusi

Kontribusi selalu diterima! Jika Anda ingin berkontribusi:

1. Fork repositori
2. Buat branch baru
3. Commit perubahan Anda
4. Push ke branch
5. Buat Pull Request

## Lisensi

Project ini dilisensikan di bawah MIT License - lihat file [LICENSE](LICENSE) untuk detail.

## Authors

- **AL-Qudzzz** - *Initial work*

## Acknowledgments

- SymPy untuk perhitungan presisi eksak
- Flask untuk framework web
- Bootstrap untuk UI components
- Tkinter untuk GUI desktop

## Screenshots

[Tambahkan screenshot aplikasi di sini]

## Contact

Jika Anda memiliki pertanyaan atau saran, silakan buka issue di repositori ini.