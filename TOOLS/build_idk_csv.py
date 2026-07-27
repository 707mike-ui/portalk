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

def build_index(master_people):
    idx = {}
    for gid, info in master_people.items():
        key = (info['surname'].strip().lower(), info['given'].strip().lower(), info['birth_year'].strip())
        idx.setdefault(key, []).append(gid)
    return idx

def main():
    kathy_ftm_ged = sys.argv[1] if len(sys.argv) > 1 else 'kathy-1.ged'
    kathy_master_ged = sys.argv[2] if len(sys.argv) > 2 else 'kathy_final.ged'
    out_csv = 'idk.csv'
    ambig_csv = 'idk_ambiguous.csv'

    print(f"Parsing {kathy_ftm_ged} (portalk tree IDs)...")
    ftm_people = parse_gedcom_individuals(kathy_ftm_ged)
    print(f"Found {len(ftm_people)} individuals")

    print(f"Parsing {kathy_master_ged} (master dakdirk IDs)...")
    master_people = parse_gedcom_individuals(kathy_master_ged)
    print(f"Found {len(master_people)} individuals")

    idx = build_index(master_people)

    matched, ambiguous, unmatched = 0, 0, 0

    with open(out_csv, 'w', newline='', encoding='utf-8') as fout, \
         open(ambig_csv, 'w', newline='', encoding='utf-8') as fambig:
        writer = csv.writer(fout)
        writer.writerow(['portal ID', 'ancestry', 'surname', 'given', 'birth_year', 'NOTES'])
        awriter = csv.writer(fambig)
        awriter.writerow(['portal ID', 'surname', 'given', 'birth_year', 'candidate_count', 'candidate_dakdirk_ids'])

        for pid, info in ftm_people.items():
            clean_pid = pid.strip('@I@').strip('@')
            key = (info['surname'].strip().lower(), info['given'].strip().lower(), info['birth_year'].strip())
            candidates = idx.get(key, [])
            if len(candidates) == 1:
                dakdirk_raw = candidates[0]
                dakdirk_id = dakdirk_raw.strip('@I@').strip('@')
                url = f"https://www.ancestry.com/family-tree/person/tree/52881559/person/{dakdirk_id}/facts"
                writer.writerow([clean_pid, url, info['surname'], info['given'], info['birth_year'], ''])
                matched += 1
            elif len(candidates) > 1:
                ids = ';'.join(c.strip('@I@').strip('@') for c in candidates)
                awriter.writerow([clean_pid, info['surname'], info['given'], info['birth_year'], len(candidates), ids])
                ambiguous += 1
            else:
                unmatched += 1

    print(f"Matched: {matched}")
    print(f"Ambiguous (flagged, not guessed): {ambiguous}")
    print(f"Unmatched: {unmatched}")
    print(f"Wrote {out_csv} and {ambig_csv}")

if __name__ == "__main__":
    main()
