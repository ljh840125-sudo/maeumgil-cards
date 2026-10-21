"""블로그 원고(txt) → 구글 문서용 HTML.

사용법: python3 blog/build.py <이미지 기준 커밋 또는 브랜치>
원고 형식: 머리말(title/keywords/tags) + '===' + 본문.
본문의 [3] 은 out/<id>/card_03.png 자리, '## ' 소제목, '- ' 목록, 'Q. / A.' 질문.
"""
import glob
import html
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ref = sys.argv[1] if len(sys.argv) > 1 else "main"
IMG = f"https://raw.githubusercontent.com/ljh840125-sudo/maeumgil-cards/{ref}/out/"

CLOSING = """<hr>
<h3>심리상담과 전문치료, 두 가지 모두 중요합니다</h3>
<p>저는 심리상담을 공부하고,</p>
<p>직접 상담을 받기도 하며,</p>
<p>많은 분들을 상담해드리고 있습니다.</p>
<p>&nbsp;</p>
<p>하지만 불안, 우울, 슬픔, 눈물, 분노, 불면증이 심각하다면</p>
<p>반드시 병원을 방문하셔서</p>
<p>약물치료와 함께 전문적인 도움을 받으시길 권합니다.</p>
<p>&nbsp;</p>
<p>저 역시 사람입니다.</p>
<p>불안이 몰려오거나 슬픔과 분노로 일상이 무너질 것 같을 때,</p>
<p>병원에 가서 진료를 받고 약을 복용하며 버텨냈습니다.</p>
<p>&nbsp;</p>
<p><b>병원에 가는 것을 부끄러워하지 마세요.</b></p>
<p>그것은 용기 있는 선택이고,</p>
<p>자신을 돌보는 책임감 있는 행동입니다.</p>
<p>&nbsp;</p>
<p>누군가와 이야기가 필요하시다면,</p>
<p>언제든 편하게 상담을 요청해주세요.</p>
<p>당신의 마음을 듣겠습니다.</p>
<p>&nbsp;</p>
<p>👉 <b>마음길연구소 상담 예약</b></p>
<p><a href="https://naver.me/51u8T8Wh">https://naver.me/51u8T8Wh</a></p>
<hr>
<p><b>글쓴이 이지혜 작가</b></p>
<p>상담대학원 석사 과정중, 중독상담전공.</p>
<p>2000여 명의 직장인, 커플, 개인을 상담하며</p>
<p>현장에서 그들의 마음을 들었습니다.</p>
<p>TCI·교류분석·NLP·애착유형 등 다양한 심리평가 도구로</p>
<p>정확한 진단을 하고, 당신의 마음을 듣고,</p>
<p>실존상담으로 답을 찾아드립니다.</p>
<p>&nbsp;</p>
<p>마음길연구소 소장 · 한국심리분석협회</p>
<p>📖 공저 『나를 알고 나를 담는다』</p>
<p><a href="https://product.kyobobook.co.kr/detail/S000001718199">https://product.kyobobook.co.kr/detail/S000001718199</a></p>
<p>&nbsp;</p>
"""


# 네이버에 붙였을 때 크기: 네이버 숫자 ≈ 구글문서 pt × 1.33
# 본문 12pt(네이버 16), 소제목 14pt(네이버 19), 제목 16pt(네이버 21)
BODY = "font-size:14pt;line-height:1.9;margin:0 0 14pt 0"
STY = {
    "<h1>": '<h1 style="font-size:21pt;line-height:1.5;margin:0 0 20pt 0">',
    "<h2>": '<h2 style="font-size:18pt;line-height:1.6;margin:30pt 0 12pt 0">',
    "<h3>": '<h3 style="font-size:15pt;line-height:1.6;margin:22pt 0 10pt 0">',
    "<li>": f'<li style="{BODY};margin:0 0 8pt 0">',
    "<p>": f'<p style="{BODY}">',
}


CSS = ("<style>body,p,li,span{font-family:'Nanum Gothic';font-weight:400;color:#333333}"
       "p,li{font-size:12pt;line-height:1.8;margin:0}"
       "h1{font-size:16pt;line-height:1.5}h2{font-size:14pt;line-height:1.6;margin-top:26pt}"
       "h3{font-size:13pt;line-height:1.6;margin-top:20pt}"
       "h1,h2,h3{font-family:'Nanum Gothic';color:#222222}</style>")


def style(doc):
    # 머리 <style> 하나로 크기 지정 (구글 문서 가져오기에서 적용됨)
    return doc.replace('<meta charset="utf-8"></head>', '<meta charset="utf-8">' + CSS + '</head>', 1)


BLANK = "<p>&nbsp;</p>"
CONN = ["는데 ", "지만 ", "면서 ", "니까 ", "려면 ", "다면 ", "라면 "]


def sentences(t):
    # 문장 끝(. ? !) 뒤 공백에서 나눔. 따옴표 닫힘까지 포함
    parts, last = [], 0
    for m in re.finditer(r"[.?!][\"\u201d\u2019']?\s+", t):
        seg = t[last:m.end()]
        if seg.count('"') % 2:
            continue  # 따옴표 안에서는 끊지 않기
        parts.append(seg.strip()); last = m.end()
    parts.append(t[last:].strip())
    return [x for x in parts if x]


def wrap(s, limit=32):
    # 긴 문장은 쉼표 → 연결어미 순으로 가운데에 가까운 곳에서 한 번 끊기
    if len(s) <= limit:
        return [s]
    mid = len(s) / 2
    # 쉼표 앞 단어가 짧으면(나열: "불안, 우울,") 끊지 않기
    cands = [m.end() for m in re.finditer(r", ", s) if len(w := s[:m.start()].split()[-1]) > 3 or w.endswith(("만", "데", "고", "면", "서", "며", "니", "요", "고요"))]
    if not cands:
        for c in CONN:
            cands += [m.end() for m in re.finditer(re.escape(c), s)]
    cands = [c for c in cands if 8 <= c <= len(s) - 8 and s[:c].count('"') % 2 == 0]
    if not cands:
        return [s]
    cut = min(cands, key=lambda c: abs(c - mid))
    a, b = s[:cut].rstrip(), s[cut:].lstrip()
    return (wrap(a, limit) if len(a) > 40 else [a]) + (wrap(b, limit) if len(b) > 40 else [b])


def para(t, bold=False):
    # 문단 → 한 문장 한 줄(긴 문장은 두 줄), 문단 끝에 빈 줄
    out, pre = [], ""
    if t[:3] in ("Q. ", "A. "):
        pre, t = t[:3], t[3:]
    sens = sentences(t)
    sens[0] = pre + sens[0]
    for sen in sens:
        lines = [x.strip() for x in sen.split(" / ")] if " / " in sen else wrap(sen)  # " / " = 직접 줄바꿈
        for line in lines:
            x = inline(line)
            out.append(f"<p><b>{x}</b></p>" if bold else f"<p>{x}</p>")
    return "\n".join(out)


def inline(t):
    t = html.escape(t, quote=False)
    return re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", t)


def closing():
    # 마무리 문단도 본문처럼 한 문장 한 줄로
    def fix(m):
        inner = m.group(1)
        if "<" in inner:
            return m.group(0)
        return para(html.unescape(inner)) + "\n" + BLANK
    return re.sub(r"<p>([^\n]*?)</p>", fix, CLOSING)


def build(path):
    pid = os.path.basename(path)[:-4]
    head, body = open(path, encoding="utf-8").read().split("===", 1)
    meta = dict(l.split(": ", 1) for l in head.strip().splitlines())
    out, lst = [], False

    def close_list():
        nonlocal lst
        if lst:
            out.append("</ul>" + BLANK)
            lst = False

    for raw in body.strip().splitlines():
        l = raw.rstrip()
        m = re.fullmatch(r"\[(\d+)\]", l.strip())
        if m:
            close_list()
            n = int(m.group(1))
            f = f"{pid}/card_{n:02d}.png"
            assert os.path.exists(os.path.join(ROOT, "out", f)), f
            out.append(f'<p style="color:#9a7b4f;font-size:10pt">📷 사진 {n}번 (card_{n:02d}.png)</p>'
                       f'<p><img src="{IMG}{f}" width="420"></p>' + BLANK)
        elif l.startswith("### "):
            close_list(); out.append(f"<h3>{inline(l[4:])}</h3>" + BLANK)
        elif l.startswith("## "):
            close_list(); out.append(BLANK + f"<h2>{inline(l[3:])}</h2>" + BLANK)
        elif l.startswith("- "):
            if not lst:
                out.append("<ul>"); lst = True
            out.append(f"<li>{inline(l[2:])}</li>")
        elif l.startswith("  ") and lst:
            out[-1] = out[-1][:-5] + f"<br>{inline(l.strip())}</li>"
        elif not l.strip():
            close_list()
        elif l.startswith("Q. "):
            close_list(); out.append(para(l))
        else:
            close_list(); out.append(para(l) + "\n" + BLANK)
    close_list()

    guide = (f'<table border="1" cellpadding="8" style="border-collapse:collapse;background:#f4efe6;width:100%">'
             f'<tr><td><b>📌 올리기 전 체크 (이 상자는 블로그에 붙이지 마세요)</b><br>'
             f'· 제목: 아래 제목을 그대로 복사<br>'
             f'· 핵심 키워드: {html.escape(meta["keywords"])}<br>'
             f'· 사진: 📷 표시 자리에 카드 이미지를 블로그에서 직접 올리기 (첫 사진 = 대표 이미지)<br>'
             f'· 태그: 맨 아래 태그 10개를 블로그 태그 칸에 입력</td></tr></table>')
    tags = f'<p style="color:#5b7a6a">{html.escape(meta["tags"])}</p>'
    doc = (f'<html><head><meta charset="utf-8"></head><body>{guide}'
           f'<h1>{inline(meta["title"])}</h1>' + "\n".join(out) + CLOSING + tags + "</body></html>")
    doc = re.sub(r"(<p>&nbsp;</p>\s*){2,}", BLANK + "\n", doc)
    doc = style(doc)
    os.makedirs(os.path.join(ROOT, "blog", "html"), exist_ok=True)
    dst = os.path.join(ROOT, "blog", "html", pid + ".html")
    open(dst, "w", encoding="utf-8").write(doc)
    return pid, meta["title"], dst


if __name__ == "__main__":
    for p in sorted(glob.glob(os.path.join(ROOT, "blog", "posts", "*.txt"))):
        pid, title, dst = build(p)
        print(pid, os.path.getsize(dst), title)
