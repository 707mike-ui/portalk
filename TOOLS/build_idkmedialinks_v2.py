import csv, re, sys

def parse_gedcom_individuals(filepath):
    with open(filepath, 'r', encoding='utf-8-sig', errors='replace') as f:
        lines = f.readlines()

    people = {}
    current_id = None
    surn, givn, birth_year = None, None, None
    in_indi = False
    in_birt = False

    def flush():
        nonlocal current_id, surn, givn, birth_year
        if current_id:
            people[current_id] = {
                'surname': surn or '',
                'given': givn or '',
                'birth_year': birth_year or ''
            }
        current_id = None
        surn, givn, birth_year = None, None, None

    for line in lines:
        stripped = line.rstrip('\n')
        parts = stripped.strip().split(' ', 2)
        if not parts or parts[0] == '':
            continue
        level = parts[0]
        if level == '0':
            flush()
            in_indi = False
            in_birt = False
            if len(parts) >= 3 and parts[2] == 'INDI':
                current_id = parts[1]
                in_indi = True
            continue
        if not in_indi:
            continue
        if level == '1':
            in_birt = (len(parts) >= 2 and parts[1] == 'BIRT')
            if len(parts) >= 3 and parts[1] == 'NAME':
                m = re.match(r'^(.*?)\s*/(.*?)/', parts[2])
                if m:
                    given_full = m.group(1).strip()
                    givn = given_full.split()[0] if given_full else ''
                    surn = m.group(2).strip()
            continue
        if level == '2' and len(parts) >= 2:
            tag = parts[1]
            val = parts[2] if len(parts) > 2 else ''
            if tag == 'SURN' and not surn:
                surn = val.strip()
            elif tag == 'GIVN' and not givn:
                givn = val.strip().split()[0] if val.strip() else ''
            elif tag == 'DATE' and in_birt:
                m = re.search(r'\b(1[5-9]\d{2}|20\d{2})\b', val)
                if m:
                    birth_year = m.group(1)
    flush()
    return people

def load_media_links(filepath):
    rows = []
    with open(filepath, 'r', encoding='utf-8-sig', newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)
    return rows

def build_index(media_rows):
    idx = {}
    for row in media_rows:
        if not row.get('dakdirk_id'):
            continue
        key = (row['surname'].strip().lower(), row['given'].strip().lower(), row['birth_year'].strip())
        idx.setdefault(key, []).append(row)
    return idx

def main():
    kathy_ftm_ged = sys.argv[1] if len(sys.argv) > 1 else 'kathy-1.ged'
    media_csv = sys.argv[2] if len(sys.argv) > 2 else '../../portal/tools/IDmediaLinks.csv'
    out_csv = 'idkmediaLinks.csv'
    ambig_csv = 'idkmediaLinks_ambiguous.csv'

    print(f"Parsing {kathy_ftm_ged}...")
    kathy_people = parse_gedcom_individuals(kathy_ftm_ged)
    print(f"Found {len(kathy_people)} individuals")

    print(f"Loading {media_csv}...")
    media_rows = load_media_links(media_csv)
    idx = build_index(media_rows)

    matched, ambiguous, unmatched = 0, 0, 0

    with open(out_csv, 'w', newline='', encoding='utf-8') as fout, \
         open(ambig_csv, 'w', newline='', encoding='utf-8') as fambig:
        writer = csv.writer(fout)
        writer.writerow(['kathy_id', 'surname', 'given', 'birth_year', 'portrait_webp', 'dakdirk_id'])
        awriter = csv.writer(fambig)
        awriter.writerow(['kathy_id', 'surname', 'given', 'birth_year', 'candidate_count', 'candidate_dakdirk_ids'])

        for kid, info in kathy_people.items():
            key = (info['surname'].strip().lower(), info['given'].strip().lower(), info['birth_year'].strip())
            candidates = idx.get(key, [])
            if len(candidates) == 1:
                row = candidates[0]
                writer.writerow([kid, info['surname'], info['given'], info['birth_year'], row['portrait_webp'], row['dakdirk_id']])
                matched += 1
            elif len(candidates) > 1:
                ids = ';'.join(c['dakdirk_id'] for c in candidates)
                awriter.writerow([kid, info['surname'], info['given'], info['birth_year'], len(candidates), ids])
                ambiguous += 1
            else:
                unmatched += 1

    print(f"Matched: {matched}")
    print(f"Ambiguous (flagged, not guessed): {ambiguous}")
    print(f"Unmatched (no media on file): {unmatched}")
    print(f"Wrote {out_csv} and {ambig_csv}")

if __name__ == "__main__":
    main()
