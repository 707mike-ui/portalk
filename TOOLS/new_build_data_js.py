#!/usr/bin/env python3
"""
Parker GEN — data.js Generator (Ancestry ID version)
Reads parkerANCES.ged and the portal html/ folder.
Produces data.js with full Ancestry person numbers as keys.
"""

import os, re, json

GEDCOM   = "/Users/admin/Desktop/portal/parker.ged"
HTML_DIR = "/Users/admin/Desktop/portal/html"
OUT_JS   = "/Users/admin/Desktop/portal/data.js"

individuals = {}
families    = {}

current_id   = None
current_type = None
current_rec  = None
in_birt = in_deat = in_marr = False

def clean_name(raw):
    return raw.replace('/', '').strip()

def extract_year(date_str):
    m = re.search(r'\b(\d{4})\b', date_str)
    return m.group(1) if m else ''

def strip_id(raw):
    """Strip @ and leading I from GEDCOM IDs to get bare Ancestry number."""
    s = raw.strip('@').strip()
    if s.startswith('I') and s[1:].isdigit():
        return s[1:]
    return s

with open(GEDCOM, 'r', encoding='utf-8', errors='replace') as f:
    for raw in f:
        line = raw.rstrip('\n\r')
        parts = line.split(' ', 2)
        if len(parts) < 2:
            continue
        try:
            level = int(parts[0])
        except ValueError:
            continue
        tag   = parts[1] if len(parts) > 1 else ''
        value = parts[2] if len(parts) > 2 else ''

        if level == 0:
            in_birt = in_deat = in_marr = False
            if len(parts) >= 3 and parts[2] == 'INDI':
                current_id   = strip_id(parts[1])
                current_type = 'INDI'
                current_rec  = {
                    'name': '', 'sex': '',
                    'birth': '', 'byear': '',
                    'death': '', 'dyear': '',
                    'famc': None, 'fams': [],
                    'page': ''
                }
                individuals[current_id] = current_rec
            elif len(parts) >= 3 and parts[2] == 'FAM':
                current_id   = parts[1].strip('@').strip()  # keep F### as-is
                current_type = 'FAM'
                current_rec  = {'husb': None, 'wife': None, 'chil': [], 'marr': ''}
                families[current_id] = current_rec
            else:
                current_id = current_rec = current_type = None

        elif current_rec is not None:
            if level == 1:
                in_birt = in_deat = in_marr = False
                if current_type == 'INDI':
                    if tag == 'NAME':
                        if not current_rec['name']:
                            current_rec['name'] = clean_name(value)
                    elif tag == 'SEX':
                        current_rec['sex'] = value.strip()
                    elif tag == 'BIRT':
                        in_birt = True
                    elif tag == 'DEAT':
                        in_deat = True
                    elif tag == 'FAMC':
                        if current_rec['famc'] is None:
                            current_rec['famc'] = value.strip('@').strip()
                    elif tag == 'FAMS':
                        current_rec['fams'].append(value.strip('@').strip())
                elif current_type == 'FAM':
                    if tag == 'HUSB':
                        current_rec['husb'] = strip_id(value)
                    elif tag == 'WIFE':
                        current_rec['wife'] = strip_id(value)
                    elif tag == 'CHIL':
                        current_rec['chil'].append(strip_id(value))
                    elif tag == 'MARR':
                        in_marr = True
            elif level == 2:
                if in_birt and tag == 'DATE':
                    current_rec['birth'] = value.strip()
                    current_rec['byear'] = extract_year(value)
                if in_deat and tag == 'DATE':
                    current_rec['death'] = value.strip()
                    current_rec['dyear'] = extract_year(value)
                if in_marr and tag == 'DATE':
                    current_rec['marr'] = value.strip()

# ── Permanent FAMC corrections DISABLED (stale after GEDCOM re-export renumbering) ──────
# Disabled 2026-07-24: hardcoded family IDs no longer match post-re-export FAMC values.
# Raw parker.ged FAMC values confirmed correct for all 6 previously-patched individuals.

# ── Match html files ──────────────────────────────────────────────────────────
html_files = set(os.listdir(HTML_DIR)) if os.path.isdir(HTML_DIR) else set()

for indi_id, rec in individuals.items():
    fname = f"{indi_id}.html"
    if fname in html_files:
        rec['page'] = f"html/{fname}"
    else:
        rec['page'] = ''

# ── Write data.js ─────────────────────────────────────────────────────────────
indi_json = json.dumps(individuals, separators=(',', ':'))
fam_json  = json.dumps(families,    separators=(',', ':'))

with open(OUT_JS, 'w', encoding='utf-8') as f:
    f.write(f'const TREE={{\n  individuals:{indi_json},\n  families:{fam_json}\n}};\n')

total     = len(individuals)
with_page = sum(1 for r in individuals.values() if r['page'])
fam_count = len(families)
print(f"GEDCOM      : {GEDCOM}")
print(f"Individuals : {total}")
print(f"With page   : {with_page}")
print(f"Families    : {fam_count}")
print(f"Written to  : {OUT_JS}")
