# 06_PROTOTIPE_SMART_ATTENDANCE — Prototipe Baseline SiHADIR (Python + OpenCV)

Folder ini berisi **prototipe perangkat lunak end-to-end** pengenalan wajah real-time (*Smart Attendance System*) menggunakan Python, OpenCV (`cv2`), `face_recognition` (dlib HOG + 128-D face embedding), dan `openpyxl`.

Sesuai **Bab S2 (§2.7 Posisi Life-Cycle)** pada dokumen SRS & System Architecture **SiHADIR**, prototipe ini merupakan bukti nyata (*proof-of-concept / Engineering Development baseline*) bahwa alur inti **Enrolment → Ekstraksi Fitur (Encoding) → Verifikasi Wajah Real-Time → Rekap Kehadiran Otomatis** telah berjalan secara fungsional sebelum diperluas menjadi arsitektur sistem target `SiHADIR` (6 subsistem, 33 komponen).

---

## Pemetaan Prototipe ke Arsitektur Sistem Target SiHADIR (`S1`–`S6`)

| Berkas di Prototipe | Fungsi di Prototipe | Komponen Arsitektur Target SiHADIR (Bab S7 & S8) | Fungsi & Requirement Terkait |
| :--- | :--- | :--- | :--- |
| `register_face.py` | Form input NIM & Nama di jendela OpenCV, pemeriksaan kualitas frame (*Laplacian blur* `≥ 30.0`, kecerahan, ukuran wajah `≥ 90 px`), auto-capture 5 foto wajah. | `C1.1 Camera`, `C5.3 Enrolment UI`, `C6.2 Enrolment Module` *(pada arsitektur target diperluas dengan `C6.1 Consent Module` & penghapusan citra mentah `≤ 100 s`)*. | `F2.1 Acquire Image`, `F7.2 Enrol Template` (`SR-FR13`, `SR-OPS3`, `SR-SEC1`, `SR-SEC2`) |
| `encode_faces.py` | Membaca foto wajah per mahasiswa, mendeteksi wajah (`model="hog"`), mengekstrak vektor fitur 128-D, dan menyimpannya ke `data/encodings/encodings.pkl`. | `C1.4 Face Detection & Recognition`, `C4.1 Template DB`, `C1.7 Roster & Template Cache`. | `F2.2 Detect Face`, `F2.4 Represent Face`, `F7.2 Enrol Template` (`SR-FR3`, `SR-FR13`) |
| `attendance.py` | Stream kamera real-time (`FRAME_SCALE=0.5`), pencocokan multi-frame (`RECOGNITION_FRAMES=5`, `TOLERANCE=0.50`), cooldown anti-duplikat (`30 s`), overlay status di layar, dan pencatatan ke `attendance_YYYY-MM-DD.xlsx`. | `C1.1 Camera`, `C1.2 Compute Unit`, `C1.3 Terminal Application`, `C1.4 Face Detection & Recognition`, `C1.6 Local Record Store`, `C1.8 Display` *(pada arsitektur target diperluas dengan `C1.5 Liveness Engine`, `C1.9 Sync Agent`, & `S2 Backend Services`)*. | `F2.1`, `F2.2`, `F2.4`, `F2.5 Match Identity`, `F4.2 Buffer Record`, `F10 Present Feedback` (`SR-FR1`, `SR-FR3`, `SR-FR15`, `SR-PRF1..4`) |
| `draft-sihadir.md` & `context-diagram-sihadir.png` | Artefak analisis awal (PRJ1) yang mendokumentasikan transisi dari prototipe lokal menuju spesifikasi arsitektur sistem terintegrasi SIAKAD. | Seluruh System of Interest `SiHADIR` (`S1`–`S6`) & 7 External Entities (`E1`–`E7`). | Bab S1, S2, S3 |

---

## Struktur Direktori

```text
06_PROTOTIPE_SMART_ATTENDANCE/
├── register_face.py               ← GUI OpenCV untuk registrasi foto wajah mahasiswa baru (auto-capture 5 frame)
├── encode_faces.py                ← Generate encoding 128-D dari foto wajah ke encodings.pkl
├── attendance.py                  ← Program utama verifikasi kehadiran real-time + simpan ke Excel
├── requirements.txt               ← Daftar pustaka Python (opencv-python, face-recognition, numpy, openpyxl)
├── draft-sihadir.md               ← Dokumen analisis konsep awal & skenario operasional SiHADIR
├── context-diagram-sihadir.png    ← Diagram konteks awal SiHADIR
└── data/
    ├── faces/
    │   └── NIM_NamaLengkap/       ← Format folder: NIM_Nama (contoh: 245150307111061_Omar)
    │       └── face_01..05.jpg    ← 5 sampel foto wajah per mahasiswa
    ├── encodings/
    │   └── encodings.pkl          ← Basis data vektor fitur wajah (auto-generated oleh encode_faces.py)
    └── attendance/
        └── attendance_YYYY-MM-DD.xlsx  ← Rekap presensi harian (auto-generated oleh attendance.py)
```

---

## Cara Pakai & Menjalankan Program

### 1. Install Dependencies

```bash
cd 06_PROTOTIPE_SMART_ATTENDANCE
pip install -r requirements.txt
```

> **Catatan `dlib` (Windows):**
> Jika instalasi `face-recognition` gagal saat kompilasi `dlib`, gunakan `conda`:
> ```bash
> conda install -c conda-forge dlib
> pip install face-recognition opencv-python openpyxl
> ```

### 2. Registrasi Wajah Mahasiswa Baru (`register_face.py`)

Kamu bisa mendaftarkan wajah langsung lewat kamera dengan GUI interaktif:
```bash
python register_face.py
```
- Ketik **NIM** dan **Nama** langsung di jendela kamera (gunakan `TAB` untuk pindah kolom, `ENTER` untuk mulai capture, `ESC` untuk keluar).
- Sistem otomatis memeriksa kualitas citra (ketajaman/blur, kecerahan, dan jarak wajah) lalu mengambil **5 foto** ke `data/faces/<NIM>_<Nama>/` dan otomatis memanggil `encode_faces.py`.

*(Alternatif manual: buat folder `data/faces/NIM_Nama/` dan masukkan 2–5 foto `.jpg`/`.png` wajah yang jelas).*

### 3. Generate Encoding (`encode_faces.py`)

Jika menambahkan foto secara manual ke `data/faces/`, jalankan:
```bash
python encode_faces.py
```
Output: `data/encodings/encodings.pkl`.

### 4. Jalankan Verifikasi Presensi Real-Time (`attendance.py`)

```bash
python attendance.py
```
- Arahkan wajah ke webcam hingga kotak indikator berubah menjadi **Hijau** (5 frame berturut-turut cocok).
- Tekan `Q` untuk keluar.
- Hasil presensi otomatis tersimpan di `data/attendance/attendance_YYYY-MM-DD.xlsx`.

---

## Panduan Oprek Parameter

### A. Parameter Verifikasi (`attendance.py` baris 14–17)

| Parameter | Default | Keterangan & Cara Oprek |
| :--- | :---: | :--- |
| `COOLDOWN_SECONDS` | `30` | Jeda minimum (detik) antar pencatatan orang yang sama agar tidak tercatat ganda. |
| `FRAME_SCALE` | `0.5` | Skala pengecilan frame sebelum deteksi HOG (`0.5` = 4× lebih cepat; naikkan ke `0.75` jika kamera jauh). |
| `TOLERANCE` | `0.50` | Ambang jarak Euclidean pencocokan wajah (`0.45` = lebih ketat/FAR rendah; `0.55` = lebih longgar/FRR rendah). |
| `RECOGNITION_FRAMES` | `5` | Jumlah frame berturut-turut yang harus cocok sebelum status `"Hadir"` disimpan ke Excel. |

### B. Parameter Quality Gate Registrasi (`register_face.py` baris 20–24)

| Parameter | Default | Keterangan & Cara Oprek |
| :--- | :---: | :--- |
| `TARGET_PHOTOS` | `5` | Jumlah foto yang diambil per mahasiswa saat registrasi. |
| `AUTO_CAPTURE` | `True` | `True` = otomatis memotret saat wajah stabil dan lolos cek kualitas; `False` = tekan `SPACE` manual. |
| `BLUR_THRESHOLD` | `30.0` | Ambang variansi Laplacian minimum untuk menolak foto yang buram (*motion blur*). |
| `MIN_FACE_SIZE` | `90` | Ukuran bounding box wajah minimum (piksel) agar wajah yang terlalu jauh ditolak. |

---

## Arti Warna Indikator di Layar Kamera (`attendance.py`)

| Warna | Arti |
| :--- | :--- |
| 🟡 **Kuning** | Wajah dikenali, sedang mengakumulasi `RECOGNITION_FRAMES` (konfirmasi) atau dalam masa cooldown. |
| 🟢 **Hijau** | Verifikasi selesai — mahasiswa sudah tercatat **Hadir** di file Excel hari ini. |
| 🔴 **Merah** | Wajah tidak dikenali (jarak fitur di atas `TOLERANCE` / belum terdaftar). |
