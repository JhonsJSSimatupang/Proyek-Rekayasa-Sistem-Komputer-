#!/usr/bin/env python3
"""Generate the SiHADIR attendance-process swimlane figure (pure SVG).

Lanes follow the subsystem decomposition in sihadir_arch_spec.m so the flow
figure and the architecture figure describe the same system.
"""

from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT_DIR = HERE / "04_DIAGRAM_DAN_VISUALISASI"
if not OUT_DIR.exists():
    OUT_DIR = HERE

LANES = [
    ("Dosen", "C5.1 / C5.2", "#FDECEF", "#B03A4E"),
    ("Terminal (S1)", "C1.1-C1.11", "#E8F1FB", "#2F6FB2"),
    ("Layanan (S2)", "C2.1-C2.8", "#EAF6EC", "#2E7D4F"),
    ("Integrasi (S3)", "C3.1-C3.3", "#FFF4E5", "#B4741E"),
    ("Data (S4)", "C4.1-C4.4", "#F3EDF9", "#6B4C9A"),
]

# (lane index, step title, function id, kind)  kind: normal | decision | terminator
STEPS = [
    (0, "Buka sesi presensi", "F1.1", "terminator"),
    (2, "Buat sesi & muat roster", "F1.2", "normal"),
    (1, "Terima roster + template", "F1.2", "normal"),
    (1, "Ambil frame kamera", "F2.1", "normal"),
    (1, "Deteksi & rekognisi wajah", "F2.2 / F2.4", "normal"),
    (1, "Uji liveness (pasif + aktif)", "F2.3", "decision"),
    (1, "Cocokkan dengan template", "F2.5", "normal"),
    (1, "Catat kehadiran lokal", "F4.2", "normal"),
    (1, "Tampilkan hasil ke mahasiswa", "F10", "normal"),
    (2, "Terapkan aturan kehadiran", "F3", "normal"),
    (1, "Sinkronkan catatan ke server", "F4.3", "normal"),
    (4, "Simpan ke Attendance DB", "F4.1", "normal"),
    (2, "Susun rekap kehadiran", "F5.1", "normal"),
    (3, "Kirim rekap ke SIAKAD", "F5.2", "normal"),
    (2, "Kirim notifikasi", "F6.1 / F6.2", "normal"),
    (3, "Teruskan ke WhatsApp Gateway", "F6.1", "terminator"),
]

BOXDASH = {"decision": True, "normal": False, "terminator": False}


def esc(t):
    return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def main():
    lane_w, lane_gap = 214, 10
    margin_l, margin_t = 26, 120
    header_h = 46
    row_pitch, box_h = 62, 44
    n_rows = len(STEPS)

    width = margin_l * 2 + len(LANES) * lane_w + (len(LANES) - 1) * lane_gap
    body_h = n_rows * row_pitch + 30
    height = margin_t + body_h + 52

    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" font-family="Segoe UI, Arial, sans-serif">',
        '<defs><marker id="a" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" '
        'markerHeight="6" orient="auto-start-reverse">'
        '<path d="M 0 0 L 10 5 L 0 10 z" fill="#52606D"/></marker></defs>',
        f'<rect width="{width}" height="{height}" fill="#FFFFFF"/>',
        f'<text x="{width/2}" y="34" text-anchor="middle" font-size="17" font-weight="600" '
        f'fill="#1F2933">SiHADIR — Alur Proses Presensi (F1–F12)</text>',
        f'<text x="{width/2}" y="54" text-anchor="middle" font-size="10.5" fill="#616E7C">'
        f'setiap langkah diberi nomor fungsi sesuai S6, sehingga bisa ditelusuri ke requirement di S5</text>',
    ]

    lane_x = []
    for i, (name, comps, fill, stroke) in enumerate(LANES):
        x = margin_l + i * (lane_w + lane_gap)
        lane_x.append(x)
        out.append(f'<rect x="{x}" y="{margin_t - header_h}" width="{lane_w}" '
                   f'height="{body_h + header_h}" rx="8" fill="{fill}" opacity="0.45" '
                   f'stroke="{stroke}" stroke-width="1.1"/>')
        out.append(f'<text x="{x + lane_w/2}" y="{margin_t - 26}" text-anchor="middle" '
                   f'font-size="11.5" font-weight="700" fill="{stroke}">{esc(name)}</text>')
        out.append(f'<text x="{x + lane_w/2}" y="{margin_t - 11}" text-anchor="middle" '
                   f'font-size="8.5" fill="#616E7C">{comps}</text>')

    boxes = []
    for r, (lane, title, fn, kind) in enumerate(STEPS):
        x = lane_x[lane] + 12
        y = margin_t + 8 + r * row_pitch
        w = lane_w - 24
        boxes.append((x, y, w, box_h, lane))

    # connectors first
    for r in range(len(boxes) - 1):
        x1, y1, w1, h1, _ = boxes[r]
        x2, y2, w2, h2, _ = boxes[r + 1]
        sx, sy = x1 + w1 / 2, y1 + h1
        tx, ty = x2 + w2 / 2, y2
        if abs(sx - tx) < 1:
            d = f"M{sx},{sy} L{tx},{ty - 6}"
        else:
            mid = sy + (ty - sy) / 2
            d = f"M{sx},{sy} L{sx},{mid} L{tx},{mid} L{tx},{ty - 6}"
        out.append(f'<path d="{d}" fill="none" stroke="#52606D" stroke-width="1.3" '
                   f'marker-end="url(#a)"/>')

    # boxes
    for (x, y, w, h, lane), (_, title, fn, kind) in zip(boxes, STEPS):
        _, _, fill, stroke = LANES[lane]
        dash = ' stroke-dasharray="2 2"' if BOXDASH[kind] else ""
        out.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="6" '
                   f'fill="#FFFFFF" stroke="{stroke}" stroke-width="1.3"{dash}/>')
        out.append(f'<text x="{x + 8}" y="{y + 16}" font-size="8" font-weight="700" '
                   f'fill="{stroke}">{esc(fn)}</text>')
        out.append(f'<text x="{x + w/2}" y="{y + 32}" text-anchor="middle" font-size="9.2" '
                   f'fill="#1F2933">{esc(title)}</text>')

    # annotation for the decision step
    out.append(f'<text x="{lane_x[1] + lane_w + 4}" y="{margin_t + 8 + 5 * row_pitch + 30}" '
               f'font-size="8.5" fill="#B03A4E">gagal → tolak,</text>')
    out.append(f'<text x="{lane_x[1] + lane_w + 4}" y="{margin_t + 8 + 5 * row_pitch + 42}" '
               f'font-size="8.5" fill="#B03A4E">ulang maks. 3×</text>')

    out.append(f'<text x="{margin_l}" y="{height - 18}" font-size="9" fill="#616E7C">'
               f'Kotak putus-putus = titik keputusan (liveness). Panah = urutan langkah.</text>')
    out.append("</svg>")

    path = OUT_DIR / "fig_alur_presensi.svg"
    path.write_text("\n".join(out), encoding="utf-8")
    print(f"langkah : {len(STEPS)}")
    print(f"lane    : {len(LANES)}")
    print(f"svg     : {path.name} ({path.stat().st_size} byte, {width}x{height})")


if __name__ == "__main__":
    main()
