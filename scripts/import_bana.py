#!/usr/bin/env python3
"""Import LiyubetBot into Bana Bot, preserve all source files, then rebrand."""
from pathlib import Path
import os, re, shutil, subprocess

ROOT=Path(__file__).resolve().parents[1]
SOURCE=Path(os.environ.get("SOURCE_DIR","/tmp/liyubetbot-source"))
if not SOURCE.is_dir():
    raise SystemExit(f"Source not found: {SOURCE}")
SKIP={".git",".github"}
for item in SOURCE.iterdir():
    if item.name in SKIP: continue
    dest=ROOT/item.name
    if item.is_dir():
        shutil.copytree(item,dest,dirs_exist_ok=True)
    else:
        shutil.copy2(item,dest)

# Every user-facing and legacy brand spelling is now Bana Bot (except third-party dependencies).
replacements=[
    (r"(?i)your-liyubet-site\\.example","banabot.example"),
    (r"(?i)liyubetbot","Banabot"),
    (r"(?i)liyubet","Bana"),
    (r"(?i)kemerbet","Bana"),
    (r"(?i)kemerbot","Banabot"),
    (r"(?i)betnabet","Bana"),
    (r"(?i)betna","Bana"),
]
def brand(content):
    for old,new in replacements:
        def replace_case(match):
            source=match.group(0)
            if source.isupper(): return new.upper()
            if source.islower(): return new.lower()
            return new
        content=re.sub(old,replace_case,content)
    return content

# Rename paths from deepest first. Separate slug and class aliases to avoid broken filesystem links.
def new_path(name):
    s=name
    for a,b in [("LIYUBET","BANA"),("Liyubet","Bana"),("liyubet","bana"),
                ("KEMERBOT","BANABOT"),("Kemerbot","Banabot"),("kemerbot","banabot"),
                ("KemerBot","BanaBot"),("KEMER","BANA"),("Kemer","Bana"),("kemer","bana"),
                ("BETNA","BANA"),("Betna","Bana"),("betna","bana")]:
        s=s.replace(a,b)
    return s
for entry in sorted(ROOT.rglob("*"),key=lambda x:len(x.parts),reverse=True):
    if ".git" in entry.parts or ".github" in entry.parts or "scripts" in entry.parts: continue
    name=new_path(entry.name)
    if name!=entry.name:
        target=entry.with_name(name)
        if target.exists(): raise RuntimeError(f"Rename collision: {entry} -> {target}")
        entry.rename(target)

# Rebrand text source while leaving vendored compiled assets and binary images/fonts byte-perfect.
extensions={".php",".md",".txt",".css",".js",".json",".xml",".yml",".yaml",".html",".svg",".sql",".sh",".env",".example",".vue",".ts"}
others={"Dockerfile","Makefile",".env.example",".gitignore",".gitattributes",".editorconfig","artisan","phpunit.xml","composer.lock","package-lock.json"}
count=0
for f in ROOT.rglob("*"):
    if not f.is_file() or any(part in {".git",".github","scripts"} for part in f.parts):continue
    if not (f.suffix.lower() in extensions or f.name in others):continue
    # Don't alter the framework's minified built vendor packages.
    if "public/js/filament/" in f.as_posix() or "public/css/filament/" in f.as_posix():continue
    try: old=f.read_text(encoding="utf-8")
    except UnicodeError: continue
    new=brand(old)
    # Spaced branding in the admin UI; PHP identifiers and file references stay valid.
    new=new.replace("'Bana Studio'","'Bana Bot Studio'").replace('"Bana Studio"','"Bana Bot Studio"')
    # Reference paths must follow actual renamed filenames.
    for a,b in [("liyubet-","bana-"),("betna-","bana-"),("kemerbot-","banabot-"),
                ("LiyubetBot-","Banabot-"),("LIYUBET-","BANA-"),("KEMERBOT-","BANABOT-")]:
        new=re.sub(re.escape(a),b,new,flags=re.I)
    if f.name==".env.example":
        new=re.sub(r"^APP_NAME=.*$", "APP_NAME=\"Bana Bot\"",new,flags=re.M)
        new=re.sub(r"^DB_DATABASE=.*$", "DB_DATABASE=banabot",new,flags=re.M)
        new=re.sub(r"^DB_USERNAME=.*$", "DB_USERNAME=banabot",new,flags=re.M)
        new=re.sub(r"^DB_PASSWORD=.*$", "DB_PASSWORD=banabot",new,flags=re.M)
    if old!=new:
        f.write_text(new,encoding="utf-8")
        count+=1

# Newly distinctive UI: midnight navy, electric aqua, warm copper.
colors={
    "#6d28d9":"#008F91","#5b21b6":"#006D75","#4c1d95":"#084A58",
    "#7c3aed":"#00B7B4","#a855f7":"#30D6C9","#a78bfa":"#69DED4",
    "#f3e8ff":"#E3FAF6","#faf8ff":"#F3FAFA","#e9def7":"#D1EAE8",
    "#e9d5ff":"#CAF2EB","#ede2ff":"#DCF8F4","#f1e8ff":"#E2F8F4",
    "#eee5ff":"#E0F7F3","#32195a":"#123C4B","#231338":"#122D3A",
    "#3b0764":"#083B4A","#716783":"#57737C","#7a7190":"#57737C",
    "#2e0f5a":"#083A49","#220845":"#062C39","#3a136f":"#007F88",
    "#2a085a":"#00636D","#8e6ebd":"#26B5B4","#cfbeeb":"#B3EFE7",
    "#8766b9":"#20AAA9","#421e74":"#087C84","#63498a":"#0A7880",
    "#251936":"#122D3A","#675582":"#587780","#eee9f5":"#E2F7F4",
    "#efebf6":"#E7F7F4","#e4dcef":"#D8F0ED","#eeeafb":"#DBF5EF",
    "#8673a4":"#63868C","#e6e3ea":"#D6E8E8","#eeedf1":"#EAF1F1",
    "#f6f5f8":"#F3FAFA","#231832":"#122D3A","#6c5a89":"#57737C",
    "#7c3aed":"#00B7B4","#f5f0ff":"#E9F9F6","#ddd0fb":"#B9EEE8",
}
for f in (ROOT/"public/css").rglob("*.css"):
    if "filament" in f.parts: continue
    css=f.read_text(encoding="utf-8")
    for before,after in colors.items():css=re.sub(re.escape(before),after,css,flags=re.I)
    f.write_text(css,encoding="utf-8")
for f in (ROOT/"resources/views").rglob("*.blade.php"):
    html=f.read_text(encoding="utf-8")
    for before,after in colors.items():html=re.sub(re.escape(before),after,html,flags=re.I)
    f.write_text(html,encoding="utf-8")

theme=ROOT/"public/css/bana-identity.css"
theme.write_text("""/* Bana Bot standalone visual identity — loaded LAST across the Filament panel. */
:root {
 --bana-navy:#092F3F; --bana-dark:#062631; --bana-primary:#008F91;
 --bana-hover:#006D75; --bana-aqua:#00B7B4; --bana-copper:#E88645;
 --bana-canvas:#F3FAFA; --bana-border:#D1EAE8; --bana-ink:#122D3A;
 --ks-primary:#008F91; --ks-primary-hover:#006D75; --ks-forest:#092F3F;
 --ks-deep:#062631; --ks-mint:#E3FAF6; --ks-ink:#122D3A;
 --ks-canvas:#F3FAFA; --ks-border:#D1EAE8; --ks-focus:#00B7B4;
 --kb-green:#008F91; --kb-bg:#F3FAFA; --kb-ink:#122D3A;
 --studio-green:#008F91; --studio-green-dark:#006D75;
 --studio-green-soft:#E3FAF6; --studio-ink:#122D3A; --studio-bg:#F3FAFA;
 --kc-green:#008F91; --kc-mint:#E3FAF6; --kc-text:#122D3A;
}
body.fi-body{background:#F3FAFA!important;color:#122D3A!important}
.fi-sidebar{background:#092F3F!important;border-color:#0D4553!important}
.fi-sidebar-header{background:#092F3F!important;border-color:#0D4553!important}
.fi-sidebar-item-label,.fi-sidebar-group-label{color:#B3D8D9!important}
.fi-sidebar-item-icon{color:#9EC9CC!important}
.fi-sidebar-item-button:hover{background:#174E5C!important}
.fi-sidebar-item.fi-active .fi-sidebar-item-button{background:#006D75!important;box-shadow:inset 3px 0 #E88645!important}
.fi-sidebar-item.fi-active .fi-sidebar-item-label,.fi-sidebar-item.fi-active .fi-sidebar-item-icon{color:#FFFFFF!important}
.fi-topbar nav{background:#FFFFFF!important;border-color:#D1EAE8!important}
.fi-btn-color-primary,.fi-btn.fi-color-primary,.kb-button,.ks-action-primary,.kb-chat-send{background:#008F91!important;color:white!important}
.fi-btn-color-primary:hover,.fi-btn.fi-color-primary:hover,.kb-button:hover,.ks-action-primary:hover,.kb-chat-send:hover{background:#006D75!important}
.fi-tabs-item.fi-active,.fi-tabs-item[aria-selected=true]{color:#008F91!important}
.fi-input-wrp:focus-within{border-color:#00B7B4!important;box-shadow:0 0 0 3px #00B7B426!important}
.kb-logo>span{background:linear-gradient(135deg,#008F91,#092F3F)!important;color:#FFF!important}
.studio-dashboard-card,.fi-section,.fi-ta{border-color:#D1EAE8!important}
.kb-chat-contact.is-selected,.kb-outgoing .kb-chat-bubble{background:#DFF8F4!important;color:#092F3F!important}
.studio-tag.green,.studio-action-icon.green{color:#006D75!important;background:#DFF8F4!important}
::selection{background:#B3EFE7;color:#092F3F}
""",encoding="utf-8")

provider=ROOT/"app/Providers/Filament/AdminPanelProvider.php"
text=provider.read_text()
text=text.replace("Color::Violet","Color::Teal").replace("->brandName('Bana Studio')","->brandName('Bana Bot Studio')")
text=text.replace("->renderHook('panels::topbar.start'", "->renderHook('panels::topbar.start'")
# append to the existing group of css links before it terminates
needle="</link>" # No-op placeholder (actual link HTML is string concatenation)
idx=text.find("->renderHook('panels::topbar.start'")
if idx<0: raise RuntimeError("Panel hook missing")
# insert a new separate head hook after the first.
hook="""            ->renderHook('panels::head.end', fn () => new HtmlString('<link rel="stylesheet" href="'.asset('css/bana-identity.css').'?v=20261112bana">'))
"""
text=text[:idx]+hook+text[idx:]
provider.write_text(text)
print(f"Imported files, rebranded {count} textual files, recolored theme and appended Bana Bot identity.")
