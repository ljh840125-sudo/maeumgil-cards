"""수기 업로드 패키지: 날짜별 폴더(카드 이미지, 숏츠 영상, 업로드글.txt) → zip.
사용법: python3 tools/manual_pack.py <출력폴더> <post id> ...
"""
import datetime, glob, json, os, shutil, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DAY = "월화수목금토일"
posts, threads = {}, {}
for f in glob.glob(os.path.join(ROOT, "content", "*.json")):
    d = json.load(open(f, encoding="utf-8"))
    if "posts" in d:
        for p in d["posts"]:
            posts[p["id"]] = p
    else:
        threads.update(d)

out, ids = sys.argv[1], sys.argv[2:]
os.makedirs(out, exist_ok=True)
index = []
for pid in ids:
    p = posts[pid]
    dt = datetime.date.fromisoformat(p["date"])
    wd = dt.weekday()
    carousel = p.get("carousel", wd in (2, 6)) and not p.get("shorts_only")
    title = p["shorts_title"].split("|")[0].strip()
    name = f"{dt:%m%d}_{DAY[wd]}_{title}"[:60].replace("/", "·").replace("?", "").replace('"', "")
    dst = os.path.join(out, name)
    os.makedirs(dst, exist_ok=True)
    src = os.path.join(ROOT, "out", pid)
    shutil.copy(os.path.join(src, "shorts.mp4"), os.path.join(dst, "영상_릴스·쇼츠용.mp4"))
    if carousel or pid.startswith("extra"):
        for c in sorted(glob.glob(os.path.join(src, "card_*.png"))):
            shutil.copy(c, os.path.join(dst, "카드" + os.path.basename(c)[5:]))
    else:
        if os.path.exists(os.path.join(src, "card_01.png")):
            shutil.copy(os.path.join(src, "card_01.png"), os.path.join(dst, "카드01_쓰레드용.png"))
    tags = " ".join(p["hashtags"])
    th = p.get("threads") or threads.get(pid, "")
    ig_kind = "카드뉴스(사진 여러 장, 카드01부터 순서대로)" if (carousel or pid.startswith("extra")) else "릴스(영상)"
    txt = f"""■ {dt:%m월 %d일}({DAY[wd]}) {p['shorts_title']}

━━ 1. 인스타그램 · {ig_kind}
{p['caption']}

{tags}

━━ 2. 유튜브 쇼츠 · 영상 파일
[제목]
{p['shorts_title'][:100]}

[설명]
{p['caption']}

{' '.join(p['hashtags'][:5])} #shorts

━━ 3. 쓰레드 · {'영상' if p.get('shorts_only') or not os.path.exists(os.path.join(src, 'card_01.png')) else '카드01 이미지'} 첨부
{th}
"""
    open(os.path.join(dst, "업로드글.txt"), "w", encoding="utf-8").write(txt)
    index.append(f"{name}  →  인스타 {ig_kind}")
open(os.path.join(out, "00_순서표.txt"), "w", encoding="utf-8").write(
    "수기 업로드 순서표\n각 폴더의 '업로드글.txt'에 인스타·유튜브·쓰레드 글이 다 들어 있어요.\n\n" + "\n".join(index) + "\n")
print("\n".join(index))
