#!/usr/bin/env python3
"""
SiHADIR - Requirement traceability consistency checker.

Validates RTM_SiHADIR.csv against the ID spaces defined in S3/S5/S6/S7/S8.
Exit code 0 = all checks pass, 1 = at least one check failed.

Usage:
    python3 check_consistency.py [RTM_SiHADIR.csv]
"""
import csv
import re
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
DEFAULT_RTM = HERE / "RTM_SiHADIR.csv"
if not DEFAULT_RTM.exists():
    DEFAULT_RTM = HERE.parent / "02_DOKUMENTASI_SUMBER" / "RTM_SiHADIR.csv"
RTM = sys.argv[1] if len(sys.argv) > 1 else str(DEFAULT_RTM)

# --- ID spaces (single source of truth) --------------------------------
SN = [f"SN-{i:02d}" for i in range(1, 14)]                    # 13 needs
UC = [f"UC-{i:02d}" for i in range(1, 13)]                    # 12 use cases
FUNC = ["F1.1", "F1.2", "F2.1", "F2.2", "F2.3", "F2.4", "F2.5", "F3",
        "F4.1", "F4.2", "F4.3", "F5.1", "F5.2", "F6.1", "F6.2",
        "F7.1", "F7.2", "F7.3", "F8.1", "F8.2", "F9", "F10", "F11", "F12"]
FUNC_AGG = ["F2", "F4"]                                       # aggregate nodes
COMP = ([f"C1.{i}" for i in range(1, 12)] +
        [f"C2.{i}" for i in range(1, 9)] +
        [f"C3.{i}" for i in range(1, 4)] +
        [f"C4.{i}" for i in range(1, 5)] +
        [f"C5.{i}" for i in range(1, 4)] +
        [f"C6.{i}" for i in range(1, 4)])
IFACE = ["IF-T2B", "IF-B2S", "IF-B2SSO", "IF-T2NTP", "IF-B2GW", "IF-UI2B"] + \
        [f"IF-I{i}" for i in range(1, 11)] + ["internal"]  # "internal" = no ICD
VERIF = {"Test", "Demonstration", "Analysis", "Inspection"}
PRIO = {"M", "S", "C", "W"}
TYPES = {"Functional": 15, "Performance": 6, "Interface": 6,
         "Security": 5, "Operational": 4}

# Use cases intentionally not mapped to a requirement:
# UC-11 and UC-12 are «include» of UC-02 (liveness, matching) and are
# covered transitively by SR-FR2/SR-FR3.
UC_TRANSITIVE = {"UC-11", "UC-12"}

fails = []
warns = []


def fail(msg):
    fails.append(msg)


def warn(msg):
    warns.append(msg)


def split(cell):
    return [x.strip() for x in cell.split(";") if x.strip()]


rows = list(csv.DictReader(open(RTM, encoding="utf-8")))
if not rows:
    fail("RTM kosong")
    print("FAIL: RTM kosong")
    sys.exit(1)

# 1. unique requirement IDs
ids = [r["ReqID"] for r in rows]
dups = [k for k, v in Counter(ids).items() if v > 1]
if dups:
    fail(f"ReqID duplikat: {dups}")

# 2. no empty mandatory cell
for r in rows:
    for col in ("ReqID", "Type", "SN", "UseCase", "Function",
                "Component", "Interface", "Verification", "Priority",
                "Acceptance"):
        if not r.get(col, "").strip():
            fail(f"{r['ReqID']}: kolom {col} kosong")

# 3. ID space membership
for r in rows:
    for s in split(r["SN"]):
        if s not in SN:
            fail(f"{r['ReqID']}: SN tidak dikenal {s}")
    for u in split(r["UseCase"]):
        if u not in UC:
            fail(f"{r['ReqID']}: UC tidak dikenal {u}")
    for f in split(r["Function"]):
        if f not in FUNC + FUNC_AGG:
            fail(f"{r['ReqID']}: fungsi tidak dikenal {f}")
    for c in split(r["Component"]):
        if c not in COMP:
            fail(f"{r['ReqID']}: komponen tidak dikenal {c}")
    for i in split(r["Interface"]):
        if i not in IFACE:
            fail(f"{r['ReqID']}: interface tidak dikenal {i}")
    if r["Verification"] not in VERIF:
        fail(f"{r['ReqID']}: metode verifikasi tidak sah {r['Verification']}")
    if r["Priority"] not in PRIO:
        fail(f"{r['ReqID']}: prioritas tidak sah {r['Priority']}")

# 4. no orphan SN
used_sn = {s for r in rows for s in split(r["SN"])}
for s in SN:
    if s not in used_sn:
        fail(f"SN tanpa requirement: {s}")

# 5. no orphan function / component (bidirectional)
used_f = {f for r in rows for f in split(r["Function"])}
for f in FUNC:
    if f not in used_f:
        fail(f"fungsi tanpa requirement: {f}")
used_c = {c for r in rows for c in split(r["Component"])}
for c in COMP:
    if c not in used_c:
        fail(f"komponen tanpa requirement: {c}")

# 6. use case coverage (UC-11/UC-12 transitive)
used_uc = {u for r in rows for u in split(r["UseCase"])}
for u in UC:
    if u not in used_uc and u not in UC_TRANSITIVE:
        fail(f"use case tanpa requirement: {u}")

# 7. acceptance criterion must carry a measurable value
for r in rows:
    if not re.search(r"\d", r["Acceptance"]):
        fail(f"{r['ReqID']}: acceptance tanpa angka terukur")

# 8. type distribution matches S5
dist = Counter(r["Type"] for r in rows)
for t, n in TYPES.items():
    if dist.get(t, 0) != n:
        fail(f"distribusi {t}: {dist.get(t,0)} != {n}")
extra = set(dist) - set(TYPES)
if extra:
    fail(f"tipe tidak dikenal: {extra}")

# 9. warnings (not blocking)
if len(rows) < 20:
    warn("jumlah requirement < 20")
if len(used_uc) < 3:
    warn("use case terpetakan < 3")

# --- report -----------------------------------------------------------
print(f"RTM          : {RTM}")
print(f"Requirements : {len(rows)}")
print(f"SN dipakai   : {len(used_sn)}/{len(SN)}")
print(f"UC dipakai   : {len(used_uc)}/{len(UC)} (transitive: {sorted(UC_TRANSITIVE)})")
print(f"Fungsi       : {len(used_f)}/{len(FUNC)} (+{len(FUNC_AGG)} agregat)")
print(f"Komponen     : {len(used_c)}/{len(COMP)}")
print(f"Interface    : {len({i for r in rows for i in split(r['Interface'])})}/{len(IFACE)}")
print(f"Distribusi   : {dict(dist)}")
print(f"Prioritas    : {dict(Counter(r['Priority'] for r in rows))}")
print(f"Verifikasi   : {dict(Counter(r['Verification'] for r in rows))}")

for w in warns:
    print(f"WARN  {w}")
for f in fails:
    print(f"FAIL  {f}")

if fails:
    print(f"\nHASIL: GAGAL ({len(fails)} temuan)")
    sys.exit(1)
print("\nHASIL: LULUS (0 temuan)")
