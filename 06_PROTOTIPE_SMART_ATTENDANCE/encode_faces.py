"""
encode_faces.py
---------------
Baca foto dari data/faces/<NIM_Nama>/face.jpg, lalu generate encoding
dan simpan ke data/encodings/encodings.pkl.

Jalankan script ini setiap kali ada wajah baru yang ditambahkan.
"""

import os
import pickle
import face_recognition
from pathlib import Path

# ─── Paths ────────────────────────────────────────────────────────────────────
BASE_DIR      = Path(__file__).parent
FACES_DIR     = BASE_DIR / "data" / "faces"
ENCODINGS_DIR = BASE_DIR / "data" / "encodings"
ENCODINGS_PKL = ENCODINGS_DIR / "encodings.pkl"

ENCODINGS_DIR.mkdir(parents=True, exist_ok=True)


# ─── Helpers ──────────────────────────────────────────────────────────────────
def parse_folder_name(folder_name: str) -> tuple[str, str]:
    """
    Parsing nama folder dengan format 'NIM_NamaLengkap'.
    Contoh: '1234567890_Budi_Santoso' → ('1234567890', 'Budi Santoso')
    """
    parts = folder_name.split("_", 1)
    nim  = parts[0]
    name = parts[1].replace("_", " ") if len(parts) > 1 else "Unknown"
    return nim, name


def load_encodings(pkl_path: Path) -> dict:
    """Load existing encodings dari file .pkl jika ada."""
    if pkl_path.exists():
        with open(pkl_path, "rb") as f:
            return pickle.load(f)
    return {}   # { nim: { "name": str, "encodings": [array, ...] } }


def save_encodings(data: dict, pkl_path: Path) -> None:
    """Simpan encodings ke file .pkl."""
    with open(pkl_path, "wb") as f:
        pickle.dump(data, f)


# ─── Core ─────────────────────────────────────────────────────────────────────
def encode_all_faces() -> None:
    existing = load_encodings(ENCODINGS_PKL)
    updated  = 0
    skipped  = 0

    if not FACES_DIR.exists():
        print(f"[ERROR] Folder '{FACES_DIR}' tidak ditemukan.")
        return

    student_dirs = [d for d in FACES_DIR.iterdir() if d.is_dir()]
    if not student_dirs:
        print("[WARN] Tidak ada folder mahasiswa di data/faces/.")
        return

    print(f"[INFO] Memproses {len(student_dirs)} mahasiswa...\n")

    for student_dir in sorted(student_dirs):
        nim, name = parse_folder_name(student_dir.name)

        # Kumpulkan semua file gambar dalam folder
        image_files = [
            f for f in student_dir.iterdir()
            if f.suffix.lower() in {".jpg", ".jpeg", ".png"}
        ]

        if not image_files:
            print(f"  [SKIP] {student_dir.name} — tidak ada gambar.")
            skipped += 1
            continue

        encodings_list = []
        for img_path in image_files:
            image = face_recognition.load_image_file(str(img_path))
            face_locs  = face_recognition.face_locations(image, model="hog")
            face_encs  = face_recognition.face_encodings(image, face_locs)

            if not face_encs:
                print(f"  [WARN] Wajah tidak terdeteksi di '{img_path.name}', dilewati.")
                continue

            # Ambil encoding wajah pertama yang ditemukan
            encodings_list.append(face_encs[0])

        if not encodings_list:
            print(f"  [SKIP] {student_dir.name} — tidak ada encoding valid.")
            skipped += 1
            continue

        existing[nim] = {"name": name, "encodings": encodings_list}
        print(f"  [OK]   {nim} | {name} — {len(encodings_list)} encoding")
        updated += 1

    save_encodings(existing, ENCODINGS_PKL)

    print(f"\n{'─'*50}")
    print(f"[DONE] {updated} mahasiswa di-encode, {skipped} dilewati.")
    print(f"[SAVE] Encodings disimpan → {ENCODINGS_PKL}\n")


# ─── Entry ────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    encode_all_faces()
