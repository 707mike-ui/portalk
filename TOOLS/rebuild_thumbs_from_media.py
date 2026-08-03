import re, os, glob

html_dir = "html"
media_dir = "media"
log_path = os.path.join(html_dir, "thumbs_rebuild_log.csv")

log_rows = [("portal_id","old_figure_count","new_figure_count","status")]

for html_path in sorted(glob.glob(os.path.join(html_dir, "*.html"))):
    fname = os.path.basename(html_path)
    m = re.match(r'^(\d{12})\.html$', fname)
    if not m:
        continue
    pid = m.group(1)

    media_files = glob.glob(os.path.join(media_dir, f"{pid}_*.webp"))
    entries = []
    for mf in media_files:
        mm = re.match(rf'^{pid}_(\d+)\.webp$', os.path.basename(mf))
        if mm:
            entries.append((int(mm.group(1)), os.path.basename(mf)))
    entries.sort(key=lambda x: x[0])

    if not entries:
        log_rows.append((pid, "N/A", "N/A", "SKIPPED_NO_MEDIA"))
        continue

    thumb_entries = entries[1:]

    with open(html_path, "r", encoding="utf-8") as f:
        content = f.read()

    old_count = content.count("<figure>")

    thumbs_match = re.search(r'(<div class="thumbs">)(.*?)(</div>)', content, re.DOTALL)
    if not thumbs_match:
        log_rows.append((pid, old_count, "N/A", "SKIPPED_NO_THUMBS_DIV"))
        continue

    figures = "".join(
        f'\n    <figure>\n      <img src="../media/{fn}" loading="lazy">\n    </figure>'
        for _, fn in thumb_entries
    )
    new_block = f'<div class="thumbs">{figures}\n  </div>' if thumb_entries else '<div class="thumbs"></div>'

    new_content = content[:thumbs_match.start()] + new_block + content[thumbs_match.end():]

    if new_content != content:
        with open(html_path + ".bak", "w", encoding="utf-8") as f:
            f.write(content)
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(new_content)
        status = "MODIFIED"
    else:
        status = "UNCHANGED"

    new_count = new_content.count("<figure>")
    log_rows.append((pid, old_count, new_count, status))

with open(log_path, "w", encoding="utf-8") as f:
    for row in log_rows:
        f.write(",".join(str(x) for x in row) + "\n")

print(f"Done. Log: {log_path}")
