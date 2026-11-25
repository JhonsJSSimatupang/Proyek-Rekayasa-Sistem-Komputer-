#!/usr/bin/env python3
"""Assemble S1..S10 into one submission-ready HTML (then Word -> PDF).

The chapters are the existing S*.md files, used verbatim so the report cannot
drift from the documents that were reviewed. This script only adds:

  * a cover page and a document-control page,
  * a table-of-contents placeholder that Word fills with real page numbers,
  * the figures (architecture, process flow, model screenshots) at the points
    where the text refers to them,
  * print CSS (A4, Times New Roman 11 pt, page break before every chapter).

Run:  python3 build_report.py
Then: powershell -File _build/to_pdf.ps1
"""

import re
import sys
from pathlib import Path

import markdown

HERE = Path(__file__).resolve().parent
OUT = HERE / "_build" / "RSK_FINAL.html"
IMG = "../"   # figures live one level up, next to the sources

CHAPTERS = [
    ("S1_Audit_PRJ2_dan_ChangeLog.md", "Audit PRJ2 & Change Log"),
    ("S2_Scope_Context.md", "Overview, Problem, Scope, Boundary, Context"),
    ("S3_Stakeholder_Needs.md", "Stakeholder & Needs"),
    ("S4_UseCase_Sequence.md", "Use Case & Sequence"),
    ("S5_Requirements.md", "Requirements (EARS)"),
    ("S6_FunctionalArch.md", "Arsitektur Fungsional"),
    ("S7_PhysicalArch.md", "Arsitektur Fisik"),
    ("S8_Allocation_N2_ICD_SPOF.md", "Alokasi, N2, ICD, SPOF"),
    ("S9_RTM_Risiko_Konsistensi.md", "RTM, Risiko, Konsistensi"),
    ("S10_Model_MATLAB.md", "Model Arsitektur di MATLAB (System Composer)"),
]

GROUP = "Kelompok Jhons"
COURSE = "CCE61317 Rekayasa Sistem dan Kebutuhan (RSK)"
DOC_VERSION = "1.0"
DOC_DATE = "25 November 2026"

# Figures are inserted right after the heading given here (raw HTML is passed
# through by markdown untouched).
FIGURES = {
    "S6_FunctionalArch.md": [
        ("## 6.5 FFD — alur fungsi utama",
         '<figure><img src="../fig_alur_presensi.png" style="width:100%">'
         '<figcaption>Gambar 6.1 &mdash; Alur proses presensi SiHADIR: 16 langkah '
         '(F1.1&ndash;F12) pada lima lane subsistem, dengan nomor fungsi yang dapat '
         'ditelusuri ke requirement di S5.</figcaption></figure>'),
    ],
    "S7_PhysicalArch.md": [
        ("## 7.2 Struktur sistem",
         '<figure><img src="../fig_arsitektur_sihadir.png" style="width:100%">'
         '<figcaption>Gambar 7.1 &mdash; Dekomposisi fisik SiHADIR: 6 subsistem, '
         '33 komponen, beserta jumlah link keluar/masuk tiap subsistem. Arah dan '
         'nama antarmuka tiap tautan ada pada tabel N2 (S8).</figcaption></figure>'),
    ],
    "S10_Model_MATLAB.md": [
        ("## 10.4 Pemeriksaan spesifikasi",
         '<figure><img src="../SiHADIR_root.png" style="width:100%">'
         '<figcaption>Gambar 10.1 &mdash; Diagram root <i>SiHADIR_Architecture.slx</i> '
         'sebagaimana tersimpan: 6 subsistem, 30 port batas, 15 kabel antarsubsistem. '
         'Diekspor langsung dari model, bukan digambar ulang.</figcaption></figure>'),
        ("## 10.8 Port yang tidak tersambung",
         '<h3>Diagram tiap subsistem</h3>'
         + "".join(
             f'<figure><img src="../{f}" style="width:100%">'
             f'<figcaption>Gambar 10.{i + 1} &mdash; {cap}</figcaption></figure>'
             for i, (f, cap) in enumerate([
                 ("SiHADIR_S1_Edge_Terminal.png", "S1 Edge Terminal: 11 komponen, 4 port batas."),
                 ("SiHADIR_S2_Backend_Services.png", "S2 Backend Services: 8 komponen, 11 port batas."),
                 ("SiHADIR_S3_Integration_Comms.png", "S3 Integration &amp; Comms: 4 komponen, 4 port batas."),
                 ("SiHADIR_S4_Data_Management.png", "S4 Data Management: 4 komponen, 5 port batas."),
                 ("SiHADIR_S5_User_Interfaces.png", "S5 User Interfaces: 3 komponen, 3 port batas."),
                 ("SiHADIR_S6_Identity_Privacy.png", "S6 Identity &amp; Privacy: 3 komponen, 3 port batas."),
             ])
         )),
    ],
}

CSS = """
@page { size: A4; margin: 2.5cm 2.2cm 2.5cm 2.2cm; }
body { font-family: "Times New Roman", serif; font-size: 11pt; line-height: 1.32;
       color: #111; text-align: justify; }
h1 { font-family: Arial, sans-serif; font-size: 17pt; color: #12395B;
     border-bottom: 2px solid #12395B; padding-bottom: 4pt; margin: 0 0 12pt 0; }
h2 { font-family: Arial, sans-serif; font-size: 13pt; color: #12395B;
     margin: 16pt 0 6pt 0; page-break-after: avoid; }
h3 { font-family: Arial, sans-serif; font-size: 11.5pt; color: #234; 
     margin: 12pt 0 4pt 0; page-break-after: avoid; }
h4 { font-family: Arial, sans-serif; font-size: 10.5pt; margin: 10pt 0 3pt 0; }
p  { margin: 0 0 6pt 0; }
ul, ol { margin: 0 0 6pt 0; padding-left: 18pt; }
li { margin-bottom: 2pt; }
code { font-family: Consolas, monospace; font-size: 9pt; background: #F2F4F7;
       padding: 0 2pt; }
pre { font-family: Consolas, monospace; font-size: 8.5pt; background: #F7F8FA;
      border: 1px solid #D5DAE0; border-left: 3px solid #12395B;
      padding: 6pt 8pt; margin: 6pt 0 8pt 0; white-space: pre-wrap;
      line-height: 1.22; page-break-inside: avoid; }
table { border-collapse: collapse; width: 100%; font-size: 8.6pt;
        font-family: Arial, sans-serif; margin: 6pt 0 10pt 0;
        page-break-inside: auto; }
th { background: #E7EDF3; border: 1px solid #9AA8B6; padding: 3pt 4pt;
     text-align: left; font-weight: 600; }
td { border: 1px solid #B7C2CD; padding: 3pt 4pt; vertical-align: top; }
tr { page-break-inside: avoid; }
blockquote { margin: 6pt 0 6pt 14pt; padding: 4pt 8pt; border-left: 3px solid #C6A15B;
             background: #FDF8EC; font-size: 10pt; }
figure { margin: 8pt 0 12pt 0; page-break-inside: avoid; text-align: center; }
figure img { max-width: 100%; }
figcaption { font-family: Arial, sans-serif; font-size: 9pt; color: #333;
             text-align: center; margin-top: 4pt; font-style: italic; }
.chapter { page-break-before: always; }
.cover { text-align: center; }
.cover .rule { border-top: 3px double #12395B; margin: 14pt 0; }
.cover h1 { border: none; font-size: 26pt; text-align: center; margin: 0; }
.cover .sub { font-size: 15pt; color: #12395B; margin: 6pt 0 0 0; }
.cover .meta { font-size: 11pt; color: #333; }
.meta-table { width: 78%; margin: 22pt auto 0 auto; font-size: 10.5pt;
              font-family: "Times New Roman", serif; }
.meta-table td { border: none; padding: 3pt 4pt; }
.meta-table td.k { width: 34%; font-weight: 600; }
"""

COVER = f"""
<div class="cover">
  <p class="meta" style="margin-bottom:26pt">{COURSE}</p>
  <div class="rule"></div>
  <p class="sub">Software Requirements Specification</p>
  <h1>SiHADIR</h1>
  <p class="sub" style="font-size:13pt">Sistem Presensi Mahasiswa Berbasis Pengenalan Wajah</p>
  <div class="rule"></div>
  <table class="meta-table">
    <tr><td class="k">Mata kuliah</td><td>{COURSE}</td></tr>
    <tr><td class="k">Kelompok</td><td>{GROUP}</td></tr>
    <tr><td class="k">Anggota</td><td>1. &hellip; (NIM &hellip;)<br>2. &hellip; (NIM &hellip;)<br>3. &hellip; (NIM &hellip;)</td></tr>
    <tr><td class="k">Versi dokumen</td><td>{DOC_VERSION}</td></tr>
    <tr><td class="k">Tanggal</td><td>{DOC_DATE}</td></tr>
  </table>
  <p style="margin-top:40pt;font-size:10pt;color:#555">
    Dokumen ini disusun dari rantai rekayasa yang dapat diperiksa ulang:<br>
    Problem &rarr; Stakeholder Needs &rarr; Use Case &rarr; Requirement &rarr; Fungsi
    &rarr; Arsitektur &rarr; Komponen &rarr; Interface &rarr; Verifikasi &rarr; Acceptance.
  </p>
</div>
"""

CONTROL = """
<div class="chapter">
<h1>Kendali Dokumen</h1>
<table>
<tr><th style="width:22%">Versi</th><th style="width:22%">Tanggal</th><th style="width:26%">Status</th><th>Perubahan</th></tr>
<tr><td>0.1</td><td>November 2026</td><td>Draf</td><td>Audit PRJ2, penetapan scope dan stakeholder needs.</td></tr>
<tr><td>0.5</td><td>November 2026</td><td>Draf</td><td>Use case, sequence, dan 36 requirement EARS.</td></tr>
<tr><td>0.8</td><td>November 2026</td><td>Draf</td><td>Arsitektur fungsional dan fisik, alokasi, N2, ICD, SPOF.</td></tr>
<tr><td>1.0</td><td>25 November 2026</td><td>Final</td><td>RTM, register risiko, model System Composer terverifikasi, konsistensi silang.</td></tr>
</table>

<h2>Ringkasan angka</h2>
<table>
<tr><th>Aspek</th><th>Jumlah</th><th>Bukti</th></tr>
<tr><td>Stakeholder / stakeholder need</td><td>7 / 13</td><td>S3</td></tr>
<tr><td>Use case rinci / sequence diagram</td><td>4 / 4</td><td>S4</td></tr>
<tr><td>Requirement (EARS)</td><td>36</td><td>S5, RTM_SiHADIR.csv</td></tr>
<tr><td>Fungsi</td><td>12 kelompok (F1&ndash;F12)</td><td>S6</td></tr>
<tr><td>Subsistem / komponen / port</td><td>6 / 33 / 64</td><td>S7, model</td></tr>
<tr><td>Interface / link / alokasi</td><td>16 / 22 / 24</td><td>S8, dictionary, model</td></tr>
<tr><td>Pemeriksaan spesifikasi</td><td>15 &mdash; LULUS</td><td>S10</td></tr>
<tr><td>Pemeriksaan model <code>.slx</code></td><td>9 &mdash; LULUS</td><td>S10</td></tr>
<tr><td>Risiko terdaftar</td><td>6</td><td>S9</td></tr>
</table>

<h2>Daftar isi</h2>
<p>[[TOC]]</p>
</div>
"""


def md_to_html(text):
    html = markdown.markdown(
        text,
        extensions=["tables", "fenced_code", "sane_lists", "nl2br"],
        output_format="html5",
    )
    # pastikan setiap heading level-1 (h1) memulai halaman baru
    html = re.sub(r"<h1([^>]*)>", lambda m: "<h1" + m.group(1) + ' style="page-break-before: always">', html)
    return html


def insert_figures(name, text):
    for anchor, block in FIGURES.get(name, []):
        if anchor not in text:
            print(f"  ! anchor tidak ditemukan di {name}: {anchor}", file=sys.stderr)
            continue
        head, tail = text.split(anchor, 1)
        # keep the heading, drop the rest of its line, then the figure
        line_end = tail.find("\n")
        title = tail[:line_end] if line_end >= 0 else ""
        rest = tail[line_end + 1:] if line_end >= 0 else ""
        text = f"{head}{anchor}{title}\n\n{block}\n\n{rest}"
    return text


def main():
    OUT.parent.mkdir(parents=True, exist_ok=True)
    parts = [
        "<!DOCTYPE html><html><head><meta charset=\"utf-8\">"
        f"<title>SiHADIR SRS &mdash; {GROUP}</title><style>{CSS}</style></head><body>",
        COVER,
        CONTROL,
    ]
    for name, title in CHAPTERS:
        path = HERE / name
        if not path.exists():
            sys.exit(f"bab tidak ditemukan: {path}")
        text = insert_figures(name, path.read_text(encoding="utf-8"))
        parts.append(md_to_html(text))
        print(f"  + {name} -> {title}")
    parts.append("</body></html>")
    OUT.write_text("\n".join(parts), encoding="utf-8")
    print(f"\nHTML: {OUT} ({OUT.stat().st_size} byte)")


if __name__ == "__main__":
    main()
