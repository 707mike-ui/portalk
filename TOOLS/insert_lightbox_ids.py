import os, re, glob

HTML_DIR = "/Users/admin/Desktop/portalk/html"
OLD = '<div class="portrait-wrap"><!-- no media yet --></div><div class="thumbs"></div></div>'

count = 0
skipped = []
for path in glob.glob(os.path.join(HTML_DIR, "*.html")):
    fname = os.path.basename(path)
    m = re.match(r'^(\d{12})\.html$', fname)
    if not m:
        continue
    pid = m.group(1)
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    if OLD not in content:
        skipped.append(fname)
        continue
    new = (
        '<div class="portrait-wrap"><img loading="lazy" src="../media/%s_1.webp"/></div><div class="thumbs">\n'
        '    <figure>\n'
        '      <img src="../media/%s_2.webp" loading="lazy">\n'
        '    </figure>\n'
        '    <figure>\n'
        '      <img src="../media/%s_3.webp" loading="lazy">\n'
        '    </figure>\n'
        '  </div></div>'
    ) % (pid, pid, pid)
    content = content.replace(OLD, new)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    count += 1

print(f"Updated: {count}")
print(f"Skipped (no placeholder found): {len(skipped)}")
if skipped:
    print("Skipped files:", skipped)
