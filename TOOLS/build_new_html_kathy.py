#!/usr/bin/env python3
"""
build_new_html.py — ADD PERSON TO PORTAL, Step 3 (page creation)

Generates html/[AncestryNumber].html for a new person using:
  - data.js (individuals + families) for name/dates/relationships
  - the locked template structure (292792337077.html) for CSS/lightbox/layout

USAGE:
  python3 build_new_html.py <AncestryNumber> --photos N

  <AncestryNumber>  ID of the new person (must already exist in data.js —
                     run new_build_data_js.py first).
  --photos N         Number of media files already placed in portal/media/
                     as [AncestryNumber]_1.webp ... [AncestryNumber]_N.webp.
                     Default 0 (no media yet — portrait/thumbs left empty,
                     page still valid, re-run later with correct N once
                     media is added).

R4 (no invention): if the person's name/dates/relationships are missing
or malformed in data.js, this script stops and reports the gap rather
than guessing.

PATHS (edit only if the portal directory moves):
"""

import json
import re
import sys
import argparse
from pathlib import Path

PORTAL_DIR = Path("/Users/admin/Desktop/portalk")
DATA_JS = PORTAL_DIR / "data.js"
HTML_DIR = PORTAL_DIR / "html"


def load_tree():
    text = DATA_JS.read_text(encoding="utf-8")
    m = re.search(r"const TREE\s*=\s*(\{.*\});?\s*$", text, re.S)
    if not m:
        sys.exit("ERROR: could not locate 'const TREE = {...}' in data.js — file format unexpected. No file written.")
    raw = m.group(1)
    raw = re.sub(r'(?<=[{,\s])individuals:', '"individuals":', raw, count=1)
    raw = re.sub(r'(?<=[{,\s])families:', '"families":', raw, count=1)
    try:
        return json.loads(raw)
    except json.JSONDecodeError as e:
        sys.exit(f"ERROR: data.js did not parse as valid JSON ({e}). No file written.")


def person_link(tree, pid):
    """Return (name, byear) for a person ID, or None if missing."""
    p = tree["individuals"].get(pid)
    if not p:
        return None
    return p.get("name", "UNKNOWN"), p.get("byear", "")


def build_pc_card(tree, pid):
    ind = tree["individuals"][pid]
    name = ind.get("name", "")
    byear = ind.get("byear", "")
    sex = ind.get("sex", "")

    rows = []

    # Father / Mother via famc
    famc = ind.get("famc")
    if famc:
        fam = tree["families"].get(famc)
        if fam is None:
            print(f"WARNING: famc '{famc}' referenced by {pid} not found in families. Skipping parent rows.")
        else:
            for role, label in (("husb", "Father"), ("wife", "Mother")):
                pid2 = fam.get(role)
                if pid2:
                    link = person_link(tree, pid2)
                    if link:
                        pname, pyear = link
                        rows.append(
                            f'<p class="pc-rel"><span class="pc-lbl">{label}</span> - '
                            f'<a href="{pid2}.html">{pname}</a> <span class="pc-year">{pyear}</span></p>'
                        )
                    else:
                        print(f"WARNING: {label} ID '{pid2}' in family {famc} not found in individuals. Row skipped.")

    # Spouse(s) + children via fams
    for fam_id in ind.get("fams", []):
        fam = tree["families"].get(fam_id)
        if fam is None:
            print(f"WARNING: fams '{fam_id}' referenced by {pid} not found in families. Skipping.")
            continue
        # spouse = the opposite-role person in this family
        if sex == "M":
            spouse_id, label = fam.get("wife"), "Wife"
        elif sex == "F":
            spouse_id, label = fam.get("husb"), "Husband"
        else:
            spouse_id, label = None, "Spouse"
            print(f"WARNING: {pid} has no/unknown sex — spouse label defaulted to 'Spouse'. Verify manually.")

        if spouse_id:
            link = person_link(tree, spouse_id)
            if link:
                sname, syear = link
                rows.append(
                    f'<p class="pc-rel"><span class="pc-lbl">{label}</span> - '
                    f'<a href="{spouse_id}.html">{sname}</a> <span class="pc-year">{syear}</span></p>'
                )
            else:
                print(f"WARNING: spouse ID '{spouse_id}' in family {fam_id} not found in individuals. Row skipped.")

        for child_id in fam.get("chil", []):
            link = person_link(tree, child_id)
            if link:
                cname, cyear = link
                rows.append(
                    f'<p class="pc-rel">Child - <a href="{child_id}.html">{cname}</a> '
                    f'<span class="pc-year">{cyear}</span></p>'
                )
            else:
                print(f"WARNING: child ID '{child_id}' in family {fam_id} not found in individuals. Row skipped.")

    pc_card = (
        f'<div class="pc-card">\n'
        f'<p class="pc-name">{name} <span style="font-size:1.0rem;">{byear}</span></p>\n'
        + "\n".join(rows) + "\n"
        f'</div>'
    )
    return pc_card, name


def build_media_block(pid, photo_count):
    if photo_count <= 0:
        return '<div class="portrait-wrap"><!-- no media yet --></div><div class="thumbs"></div>'
    portrait = f'<div class="portrait-wrap"><img loading="lazy" src="../media/{pid}_1.webp"/></div>'
    thumbs = ['<div class="thumbs">']
    for n in range(2, photo_count + 1):
        thumbs.append(
            f'    <figure>\n      <img src="../media/{pid}_{n}.webp" loading="lazy">\n    </figure>'
        )
    thumbs.append('  </div>')
    return portrait + "\n".join(thumbs)


PAGE_TEMPLATE = """<!DOCTYPE html>

<html lang="en">
<head>
<meta charset="utf-8"/>
<meta content="width=device-width,initial-scale=1" name="viewport"/>
<title>{title}</title>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Georgia, serif;
    background: #f5f0e8; color: #222; line-height: 1.5;
    min-width: 0; overflow-x: hidden;
    min-height: 100dvh; display: flex; flex-direction: column;
  }}
  a {{ color: #5a3e1b; text-decoration: none; transition: 0.2s; }}
  header {{
    background: #3b2a1a; color: #f5f0e8; padding: 0.75rem 0.5rem;
    display: flex; align-items: center; justify-content: space-between;
    font-family: Georgia, serif; line-height: 1; width: 100%;
  }}
  header h1 {{ font-size: 1rem; line-height: 1; margin: 0; padding: 0; }}
  .container {{
    max-width: 1200px; width: 100%; margin: 0 auto; padding: 8px 16px;
    box-sizing: border-box; flex: 1; display: flex; flex-direction: column;
  }}
  h2 {{
    font-size: clamp(1.1rem, 4vw, 1.4rem);
    border-bottom: 2px solid #c8a96e;
    margin: 24px 0 12px; padding-bottom: 6px; color: #3b2a1a;
  }}
  .portrait-wrap {{
    flex: 0 0 auto; display: flex; align-items: flex-start;
    justify-content: center; padding: 8px 0;
  }}
  .portrait-wrap img {{
    width: 100%; max-width: 800px; display: block;
    border-radius: 8px; object-fit: contain; object-position: center top;
    height: auto; max-height: 70vh;
  }}
  .thumbs figure {{
    background: #fff; border: 1px solid #ddd; border-radius: 8px;
    padding: 4px; overflow: hidden;
  }}
  .thumbs img {{
    width: 100%; height: auto; aspect-ratio: 1/1; object-fit: cover;
    object-position: center top;
    border-radius: 4px; cursor: pointer; display: block;
    transition: transform 0.25s ease;
  }}
  .thumbs figure img:hover {{ transform: scale(1.08); }}
  .thumbs figcaption {{ font-size: 0.75rem; color: #555; margin-top: 4px; text-align: center; }}
  #lb {{
    display: none; position: fixed; inset: 0; background: rgba(0,0,0,0.95);
    z-index: 9999; overflow-y: auto; overflow-x: hidden;
  }}
  #lb.open {{ display: block; }}
  #lb-img {{ width: 100vw; max-width: 100vw; height: auto; max-height: none; object-fit: contain; outline: none;
             border: none; user-select: none; -webkit-user-select: none; -webkit-user-drag: none;
             margin: 60px 0 40px; display: block; }}
  #lb-cap {{ color: #eee; margin: 16px auto 40px; font-size: 1rem; text-align: center; width: 95vw; }}
  #lb-close {{
    position: fixed; top: 16px; right: 16px; font-size: 2rem; color: #fff;
    border: none; cursor: pointer; background: rgba(0,0,0,0.75); border-radius: 50%;
    width: 44px; height: 44px; line-height: 44px; text-align: center; padding: 0;
    z-index: 10001;
  }}
  .pc-card  {{ background:#fff; border:1px solid #ddd; border-radius:8px;
               padding:8px 16px; margin:8px auto;
               box-shadow:0 2px 4px rgba(0,0,0,.05); text-align:center; flex-shrink:0; }}
  .pc-name  {{ font-size:1.4rem; font-weight:bold; color:#3b2a1a; margin:0 0 2px; line-height:1.2; }}
  .pc-dates {{ color:#666; font-size:.88rem; margin:0 0 6px; }}
  .pc-rel   {{ margin:2px 0; font-size:.93rem; }}
  .pc-lbl   {{ font-weight:bold; color:#5a3e1b; }}
  .pc-year  {{ font-size:0.78rem; }}
.thumbs {{
  display: grid; grid-template-columns: repeat(2, minmax(0, 396px));
  justify-content: center;
  gap: 8px; margin-bottom: 8px; flex-shrink: 0;
}}
.portrait-wrap img.is-portrait {{
    width: 100%; height: auto; max-height: none;
    max-width: 800px;
  }}
</style>
</head>
<body>
<script src="header-h.js"></script>
<div class="container">
{pc_card}

<!-- ==================== LIGHTBOX START ==================== -->
{media_block}</div>

<!-- ==================== LIGHTBOX STOP ==================== -->
<div id="lb">
<button id="lb-close">&times;</button>
<button id="lb-prev">&lsaquo;</button>
<img id="lb-img" src=""/>
<button id="lb-next">&rsaquo;</button>
<div id="lb-cap"></div>
</div>
<style>
#lb-prev, #lb-next {{
  position: fixed; top: 50%; transform: translateY(-50%);
  font-size: 3rem; color: #fff; background: rgba(0,0,0,0.45);
  border: none; cursor: pointer; border-radius: 50%;
  width: 54px; height: 54px; line-height: 54px; text-align: center;
  padding: 0; z-index: 10000; user-select: none;
  transition: background 0.2s;
}}
#lb-prev {{ left: 16px; }}
#lb-next {{ right: 16px; }}
#lb-prev:hover, #lb-next:hover {{ background: rgba(0,0,0,0.75); }}
</style>
<script>
(function(){{
  var pImg=document.querySelector('.portrait-wrap img');
  if(pImg){{function chk(){{if(pImg.naturalHeight>pImg.naturalWidth)pImg.classList.add('is-portrait');}}
  if(pImg.complete&&pImg.naturalWidth)chk();else pImg.addEventListener('load',chk);}}
}})();
</script>
<script>(function(){{
  var lb=document.getElementById('lb'),
      lbImg=document.getElementById('lb-img'),
      lbCap=document.getElementById('lb-cap'),
      allImgs=Array.from(document.querySelectorAll('.portrait-wrap img, .thumbs figure img')),
      cur=0, touchStartX=0;
  function show(i){{
    cur=(i+allImgs.length)%allImgs.length;
    var img=allImgs[cur];
    lbImg.src=img.src; lbImg.alt=img.alt;
    lbCap.textContent=img.alt||'';
  }}
  allImgs.forEach(function(img,i){{
    img.addEventListener('click',function(){{ show(i); lb.classList.add('open'); }});
  }});
  document.getElementById('lb-close').addEventListener('click',function(){{lb.classList.remove('open');}});
  document.getElementById('lb-prev').addEventListener('click',function(e){{e.stopPropagation();show(cur-1);}});
  document.getElementById('lb-next').addEventListener('click',function(e){{e.stopPropagation();show(cur+1);}});
  lb.addEventListener('click',function(e){{if(e.target===lb)lb.classList.remove('open');}});
  document.addEventListener('keydown',function(e){{
    if(!lb.classList.contains('open'))return;
    if(e.key==='Escape')lb.classList.remove('open');
    if(e.key==='ArrowLeft')show(cur-1);
    if(e.key==='ArrowRight')show(cur+1);
  }});
  lb.addEventListener('touchstart',function(e){{touchStartX=e.changedTouches[0].screenX;}},{{passive:true}});
  lb.addEventListener('touchend',function(e){{
    var dx=e.changedTouches[0].screenX-touchStartX;
    if(Math.abs(dx)>40){{dx<0?show(cur+1):show(cur-1);}}
  }},{{passive:true}});
}})();
</script>
</body>
</html>"""


def main():
    ap = argparse.ArgumentParser(description="Generate a new person page from data.js + locked template.")
    ap.add_argument("ancestry_id", help="AncestryNumber of the new person (must exist in data.js)")
    ap.add_argument("--photos", type=int, default=0, help="Number of media files already in portal/media/ (default 0)")
    args = ap.parse_args()

    if not DATA_JS.exists():
        sys.exit(f"ERROR: {DATA_JS} not found. No file written.")

    tree = load_tree()
    pid = args.ancestry_id

    if pid not in tree["individuals"]:
        sys.exit(f"ERROR: '{pid}' not found in data.js individuals. Run new_build_data_js.py first. No file written.")

    out_path = HTML_DIR / f"{pid}.html"
    if out_path.exists():
        sys.exit(f"ERROR: {out_path} already exists. This script will not overwrite. Delete/rename it first if regeneration is intended.")

    pc_card, name = build_pc_card(tree, pid)
    media_block = build_media_block(pid, args.photos)
    page = PAGE_TEMPLATE.format(title=name, pc_card=pc_card, media_block=media_block)

    out_path.write_text(page, encoding="utf-8")
    print(f"WROTE: {out_path}")
    if args.photos == 0:
        print("NOTE: --photos was 0 — portrait/thumbs left empty. Re-run after Step 4 (media add) with correct --photos N, or hand-edit the media block.")


if __name__ == "__main__":
    main()
