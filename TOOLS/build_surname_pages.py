import re

TEMPLATE_PATH = "/Users/admin/Desktop/portal/html/surname/Adrian.html"
OUT_DIR = "/Users/admin/Desktop/portalk/html/surname"
LIST_PATH = "/Users/admin/Desktop/portalk/TOOLS/surnames_filtered.txt"

with open(TEMPLATE_PATH, 'r', encoding='utf-8') as f:
    template = f.read()

with open(LIST_PATH, 'r', encoding='utf-8') as f:
    surnames = [line.strip() for line in f if line.strip()]

count = 0
for surname in surnames:
    out = template
    out = out.replace(
        "<title>Adrian — Dirksen / Parker Family Tree</title>",
        f"<title>{surname} — Dirksen / Hie Family Tree</title>"
    )
    out = out.replace("var SURNAME = 'Adrian';", f"var SURNAME = '{surname}';")
    out_path = f"{OUT_DIR}/{surname}.html"
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(out)
    count += 1

print(f"Generated: {count} surname pages")
