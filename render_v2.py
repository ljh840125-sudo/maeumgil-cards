"""카드뉴스 v2 디자인 (2026-11-09~): 크림 종이 + 흰 카드 프레임 + 주아체 제목 + 아이콘 박스.

render.py 가 post["design"] == "v2" (또는 주간 파일의 "design": "v2") 일 때 이 모듈을 쓴다.
새 슬라이드 타입: grid4(2x2 개념 상자), rows3(아이콘 줄 상자), 그리고 기존 cover/text/list/vs/quote/cta/next/booking.
제목 안의 [단어] 는 포인트 색으로 칠해진다.  slide["icon"] 으로 제목 위 아이콘, slide["image"] 로 그림(art/…png) 삽입.
"""
import math
import os
import random
import re
import sys

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = os.path.dirname(os.path.abspath(__file__))
F = os.path.join(ROOT, "fonts")
JUA = os.path.join(F, "Jua.ttf")

SANS = {w: os.path.join(F, f"Pretendard-{w}.otf") for w in ("Regular", "SemiBold", "Bold", "ExtraBold")}
_fc = {}
_cmap = {}


def font(p, s):
    if (p, s) not in _fc:
        _fc[(p, s)] = ImageFont.truetype(p, s)
    return _fc[(p, s)]


def has_glyphs(path, text):
    if path not in _cmap:
        from fontTools.ttLib import TTFont
        _cmap[path] = set(TTFont(path).getBestCmap().keys())
    return all(ord(c) in _cmap[path] or c.isspace() for c in text)


def title_font(text, size):
    # 주아체에 없는 글자가 있으면 그 줄만 프리텐다드로
    return font(JUA, size) if has_glyphs(JUA, text) else font(SANS["ExtraBold"], int(size * 0.92))


def mix(a, b, t):
    return tuple(int(x * (1 - t) + y * t) for x, y in zip(a, b))


def palette(th, dark=False):
    acc = th["accent"]
    if dark:
        p = {"paper": (34, 37, 64), "card": (44, 48, 80), "ink": (250, 244, 230), "body": (214, 212, 228),
             "muted": (160, 160, 190), "accent": acc}
        p["tint"] = mix(p["card"], acc, 0.20)
        p["grey"] = mix(p["card"], (255, 255, 255), 0.08)
        p["leaf"] = mix(p["paper"], (120, 140, 190), 0.25)
        p["bubble"] = mix(p["card"], (255, 255, 255), 0.12)
    else:
        p = {"paper": (247, 242, 233), "card": (255, 252, 246), "ink": (54, 48, 46), "body": (98, 90, 86),
             "muted": (156, 146, 138), "accent": acc}
        p["tint"] = mix(p["card"], acc, 0.16)
        p["grey"] = mix(p["card"], (120, 112, 104), 0.10)
        p["leaf"] = mix(p["paper"], (122, 150, 112), 0.35)
        p["bubble"] = (255, 255, 255)
    p["on_accent"] = th.get("button_text", (255, 255, 255))
    return p


# ---------- 아이콘 (단색 도형) ----------
def icon(d, kind, cx, cy, r, col, bg):
    w = max(3, r // 7)
    if kind == "heart":
        d.ellipse((cx - r, cy - r * 0.75, cx, cy + r * 0.2), fill=col)
        d.ellipse((cx, cy - r * 0.75, cx + r, cy + r * 0.2), fill=col)
        d.polygon([(cx - r * 0.97, cy - r * 0.1), (cx + r * 0.97, cy - r * 0.1), (cx, cy + r * 0.95)], fill=col)
    elif kind == "chat":
        d.rounded_rectangle((cx - r, cy - r * 0.8, cx + r, cy + r * 0.5), radius=int(r * 0.45), fill=col)
        d.polygon([(cx - r * 0.5, cy + r * 0.4), (cx - r * 0.1, cy + r * 0.4), (cx - r * 0.6, cy + r * 0.95)], fill=col)
        for k in (-1, 0, 1):
            d.ellipse((cx + k * r * 0.42 - r * 0.11, cy - r * 0.26, cx + k * r * 0.42 + r * 0.11, cy - r * 0.04), fill=bg)
    elif kind == "sprout":
        d.line((cx, cy + r, cx, cy - r * 0.1), fill=col, width=w + 2)
        d.ellipse((cx - r, cy - r * 0.75, cx, cy + r * 0.05), fill=col)
        d.ellipse((cx, cy - r, cx + r * 0.9, cy - r * 0.25), fill=col)
    elif kind == "shield":
        d.polygon([(cx - r * 0.8, cy - r * 0.8), (cx, cy - r), (cx + r * 0.8, cy - r * 0.8), (cx + r * 0.8, cy),
                   (cx, cy + r), (cx - r * 0.8, cy)], fill=col)
    elif kind == "check":
        d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=col)
        d.line((cx - r * 0.45, cy, cx - r * 0.1, cy + r * 0.38, cx + r * 0.5, cy - r * 0.35), fill=bg, width=w + 2, joint="curve")
    elif kind == "star":
        pts = []
        for i in range(10):
            a = -math.pi / 2 + i * math.pi / 5
            rr = r if i % 2 == 0 else r * 0.45
            pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
        d.polygon(pts, fill=col)
    elif kind == "moon":
        d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=col)
        d.ellipse((cx - r * 0.35, cy - r * 1.05, cx + r * 1.3, cy + r * 0.6), fill=bg)
    elif kind == "clock":
        d.ellipse((cx - r, cy - r, cx + r, cy + r), outline=col, width=w + 2)
        d.line((cx, cy, cx, cy - r * 0.6), fill=col, width=w + 1)
        d.line((cx, cy, cx + r * 0.45, cy + r * 0.2), fill=col, width=w + 1)
    elif kind == "people":
        for dx, s in ((-0.45, 0.8), (0.45, 0.8)):
            x = cx + dx * r
            d.ellipse((x - r * 0.3 * s, cy - r * 0.85, x + r * 0.3 * s, cy - r * 0.25), fill=col)
            d.pieslice((x - r * 0.55 * s, cy - r * 0.1, x + r * 0.55 * s, cy + r * 1.0), 180, 360, fill=col)
    elif kind == "ear":
        d.arc((cx - r * 0.7, cy - r, cx + r * 0.7, cy + r * 0.6), 160, 380, fill=col, width=w + 2)
        d.line((cx + r * 0.62, cy - r * 0.05, cx + r * 0.1, cy + r * 0.9), fill=col, width=w + 2)
        d.arc((cx - r * 0.3, cy - r * 0.5, cx + r * 0.3, cy + r * 0.1), 180, 360, fill=col, width=w)
    elif kind == "bulb":
        d.ellipse((cx - r * 0.75, cy - r, cx + r * 0.75, cy + r * 0.45), fill=col)
        d.rectangle((cx - r * 0.35, cy + r * 0.3, cx + r * 0.35, cy + r * 0.85), fill=col)
        d.line((cx - r * 0.35, cy + r * 0.58, cx + r * 0.35, cy + r * 0.58), fill=bg, width=w)
    elif kind == "pen":
        d.polygon([(cx - r * 0.85, cy + r * 0.85), (cx - r * 0.6, cy + r * 0.25), (cx + r * 0.45, cy - r * 0.8),
                   (cx + r * 0.85, cy - r * 0.4), (cx - r * 0.2, cy + r * 0.62)], fill=col)
    elif kind == "pause":
        d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=col)
        d.rectangle((cx - r * 0.38, cy - r * 0.42, cx - r * 0.12, cy + r * 0.42), fill=bg)
        d.rectangle((cx + r * 0.12, cy - r * 0.42, cx + r * 0.38, cy + r * 0.42), fill=bg)
    elif kind == "question":
        d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=col)
        d.text((cx, cy + 2), "?", font=font(SANS["ExtraBold"], int(r * 1.3)), fill=bg, anchor="mm")
    else:  # dot
        d.ellipse((cx - r * 0.5, cy - r * 0.5, cx + r * 0.5, cy + r * 0.5), fill=col)


# ---------- 글자 ----------
def wrap(d, text, fnt, max_w):
    lines, cur = [], ""
    for word in text.split(" "):
        t = (cur + " " + word).strip()
        if d.textlength(t.replace("[", "").replace("]", ""), font=fnt) <= max_w:
            cur = t
            continue
        if cur:
            lines.append(cur)
        cur = word
        while d.textlength(cur.replace("[", "").replace("]", ""), font=fnt) > max_w and len(cur) > 1:
            k = len(cur) - 1
            while k > 1 and d.textlength(cur[:k].replace("[", "").replace("]", ""), font=fnt) > max_w:
                k -= 1
            lines.append(cur[:k])
            cur = cur[k:]
    if cur:
        lines.append(cur)
    return lines


def seg_text(d, x, y, line, fnt, col, hl, anchor_center=None):
    """[강조] 구간을 포인트 색으로. anchor_center=중앙 x 이면 가운데 정렬."""
    segs = [(s, i % 2 == 1) for i, s in enumerate(re.split(r"[\[\]]", line)) if s]
    total = sum(d.textlength(s, font=fnt) for s, _ in segs)
    if anchor_center is not None:
        x = anchor_center - total / 2
    for s, on in segs:
        d.text((x, y), s, font=fnt, fill=hl if on else col)
        x += d.textlength(s, font=fnt)
    return total


class Canvas:
    def __init__(self, th, W, H, dark):
        self.W, self.H, self.P = W, H, palette(th, dark)
        self.tall = H > 1500
        P = self.P
        img = Image.new("RGB", (W, H), P["paper"])
        # 종이 결
        rnd = random.Random(W + H)
        px = img.load()
        for _ in range(W * H // 18):
            x, y = rnd.randrange(W), rnd.randrange(H)
            c = px[x, y]
            k = rnd.choice((-5, -3, 3))
            px[x, y] = tuple(max(0, min(255, v + k)) for v in c)
        # 잎 장식 (카드 뒤로 살짝)
        layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        ld = ImageDraw.Draw(layer)
        for (bx, by, ang) in ((W - 40, 70, 35), (W - 110, 20, 70), (40, H - 90, 210), (100, H - 30, 250)):
            for k in range(3):
                a = math.radians(ang + k * 28)
                lx, ly = bx + math.cos(a) * 70, by + math.sin(a) * 70
                leaf = Image.new("RGBA", (120, 60), (0, 0, 0, 0))
                ImageDraw.Draw(leaf).ellipse((0, 0, 119, 59), fill=P["leaf"] + (200,))
                leaf = leaf.rotate(-math.degrees(a), expand=True)
                layer.alpha_composite(leaf, (int(lx - leaf.width / 2), int(ly - leaf.height / 2)))
        img = Image.alpha_composite(img.convert("RGBA"), layer.filter(ImageFilter.GaussianBlur(1))).convert("RGB")
        # 카드 그림자 + 카드
        m = 44 if not self.tall else 50
        sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        ImageDraw.Draw(sh).rounded_rectangle((m + 4, m + 10, W - m + 4, H - m + 10), radius=44, fill=(60, 40, 20, 40))
        img = Image.alpha_composite(img.convert("RGBA"), sh.filter(ImageFilter.GaussianBlur(14))).convert("RGB")
        self.img = img
        self.d = ImageDraw.Draw(img)
        self.d.rounded_rectangle((m, m, W - m, H - m), radius=44, fill=P["card"])
        self.m = m
        self.X0, self.X1 = m + 62, W - m - 62
        self.CX = W // 2


def render_slide_v2(slide, th, W, H, page=None, total=None, footer=True, band=None, dark=False):
    C = Canvas(th, W, H, dark)
    d, P = C.d, C.P
    tall = C.tall
    kind = slide["type"]
    maxw = C.X1 - C.X0

    # 쪽 번호 동그라미
    if page and total:
        r = 30
        cx, cy = C.m + 58, C.m + 58
        d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=P["tint"])
        d.text((cx, cy), str(page), font=font(SANS["Bold"], 30), fill=P["accent"], anchor="mm")

    # 머리 띠(라벨): 손글씨 테이프
    top = C.m + (150 if tall else 40)
    if slide.get("label"):
        lf = font(JUA, 40 if tall else 36) if has_glyphs(JUA, slide["label"]) else font(SANS["SemiBold"], 34 if tall else 32)
        tw = d.textlength(slide["label"], font=lf)
        bh = 66 if tall else 60
        x0 = C.CX - tw / 2 - 34
        d.rounded_rectangle((x0, top, x0 + tw + 68, top + bh), radius=10, fill=P["tint"])
        d.text((C.CX, top + bh / 2 + 1), slide["label"], font=lf, fill=P["accent"] if not slide.get("label_ink") else P["ink"], anchor="mm")
    content_top = top + (130 if tall else 110)
    foot_y = H - C.m - (210 if tall else 120)
    if band:
        foot_y -= 90

    # 블록 쌓기: (높이, 그리기 함수)
    blocks = []

    def add(h, fn):
        blocks.append((h, fn))

    # 그림
    if slide.get("image"):
        p = os.path.join(ROOT, slide["image"])
        if os.path.exists(p):
            im = Image.open(p).convert("RGB")
            ih = 560 if tall else 420
            iw = int(im.width * ih / im.height)
            if iw > maxw:
                iw, ih = maxw, int(im.height * maxw / im.width)
            im = im.resize((iw, ih))
            mask = Image.new("L", (iw, ih), 0)
            ImageDraw.Draw(mask).rounded_rectangle((0, 0, iw - 1, ih - 1), radius=28, fill=255)

            def f_img(y, im=im, mask=mask, iw=iw):
                C.img.paste(im, (int(C.CX - iw / 2), int(y)), mask)
            add(ih + 40, f_img)

    if slide.get("icon") and kind not in ("grid4", "rows3"):
        ir = 46 if kind == "cover" else 38

        def f_icon(y, ir=ir):
            d.ellipse((C.CX - ir - 22, y, C.CX + ir + 22, y + 2 * ir + 44), fill=P["tint"])
            icon(d, slide["icon"], C.CX, y + ir + 22, ir, P["accent"], P["tint"])
        add(2 * ir + 44 + 34, f_icon)

    if kind == "quote" and slide.get("art"):
        import render as R
        ah = 300 if not tall else 380

        def f_art(y, ah=ah):
            R.draw_art(C.img, slide["art"], dict(th, accent=P["accent"]), (int(C.X0), int(y), int(C.X1), int(y + ah)))
        add(ah + 20, f_art)

    # 제목
    tsize = {"cover": 96, "quote": 74, "booking": 76, "cta": 80, "next": 74}.get(kind, 74)
    if tall:
        tsize = int(tsize * 1.08)
    tlines = []
    raw = [("[" + l[1:] + "]" if l.startswith("*") else l) for l in slide.get("title", [])]
    while tsize > 60 and any(d.textlength(l.replace("[", "").replace("]", ""), font=title_font(l, tsize)) > maxw for l in raw):
        tsize -= 4  # 한 줄이 넘치면 글자를 조금 줄여 줄바꿈을 피함
    for line in slide.get("title", []):
        line = "[" + line[1:] + "]" if line.startswith("*") else line
        tf = title_font(line.replace("[", "").replace("]", ""), tsize)
        for wl in wrap(d, line, tf, maxw):
            # 줄바꿈으로 괄호가 끊기면 보정
            if wl.count("[") > wl.count("]"):
                wl += "]"
            if wl.count("]") > wl.count("["):
                wl = "[" + wl
            tlines.append((wl, tf))
    if tlines:
        lh = int(tsize * 1.30)

        def f_title(y):
            for i, (wl, tf) in enumerate(tlines):
                seg_text(d, 0, y + i * lh, wl, tf, P["ink"], P["accent"], anchor_center=C.CX)
        add(len(tlines) * lh + 34, f_title)

    # 본문(가운데)
    bf = font(SANS["Regular"], 44 if tall else 38)
    blh = 70 if tall else 62
    blines = []
    for line in slide.get("sub", []) + slide.get("body", []):
        blines += wrap(d, line, bf, maxw)
    if blines:
        def f_body(y):
            for i, wl in enumerate(blines):
                col = P["accent"] if wl.startswith("→") else P["body"]
                seg_text(d, 0, y + i * blh, wl, bf, col, P["accent"], anchor_center=C.CX)
        add(len(blines) * blh + 26, f_body)

    # 목록: 칩 상자
    if slide.get("items"):
        itf = font(SANS["Regular"], 42 if tall else 37)
        ilh = 56 if tall else 50
        rows = []
        for it in slide["items"]:
            rows.append(wrap(d, it, itf, maxw - 130))
        hs = [len(r) * ilh + (44 if tall else 38) for r in rows]

        def f_items(y):
            for r, h in zip(rows, hs):
                d.rounded_rectangle((C.X0, y, C.X1, y + h), radius=26, fill=P["tint"])
                icon(d, "check", C.X0 + 50, y + h / 2, 20, P["accent"], P["tint"])
                ty = y + (h - len(r) * ilh) / 2 - 2
                for wl in r:
                    seg_text(d, C.X0 + 94, ty, wl, itf, P["ink"], P["accent"])
                    ty += ilh
                y += h + 16
        add(sum(hs) + 16 * len(hs) + 10, f_items)

    # vs: 위/아래 패널
    if kind == "vs":
        bubf = font(SANS["Regular"], 42 if tall else 36)
        blh2 = 54 if tall else 46
        pad = 24 if tall else 20
        tagf = font(SANS["Bold"], 34 if tall else 30)
        panels = []
        for key, tag_default, good in (("a", "대화가 편한 사람", True), ("b", "대화가 피곤한 사람", False)):
            if not slide.get(key):
                continue
            bubs = [wrap(d, line, bubf, int(maxw * 0.86) - 2 * pad) for line in slide[key]]
            bh = [len(b) * blh2 + 2 * pad - 8 for b in bubs]
            ph = 26 + 50 + 14 + sum(bh) + 12 * (len(bh) - 1) + 26
            panels.append((slide.get(key + "_tag", tag_default), good, bubs, bh, ph))

        def f_vs(y):
            for n, (tag, good, bubs, bh, ph) in enumerate(panels):
                fill = P["tint"] if good else P["grey"]
                d.rounded_rectangle((C.X0 - 20, y, C.X1 + 20, y + ph), radius=30, fill=fill)
                tw = d.textlength(tag, font=tagf)
                d.rounded_rectangle((C.X0, y + 22, C.X0 + tw + 40, y + 72), radius=25,
                                    fill=P["accent"] if good else P["muted"])
                d.text((C.X0 + 20, y + 47), tag, font=tagf, fill=P["on_accent"], anchor="lm")
                yy = y + 26 + 50 + 14
                for j, (b, h) in enumerate(zip(bubs, bh)):
                    bw = max(d.textlength(w, font=bubf) for w in b) + 2 * pad
                    right = j % 2 == 1
                    x0 = C.X1 - bw if right else C.X0
                    bfill = P["accent"] if (right and good) else (P["muted"] if right else P["bubble"])
                    tcol = P["on_accent"] if right else P["ink"]
                    d.rounded_rectangle((x0, yy, x0 + bw, yy + h), radius=24, fill=bfill)
                    ty = yy + pad - 4
                    for w in b:
                        d.text((x0 + pad, ty), w, font=bubf, fill=tcol)
                        ty += blh2
                    yy += h + 12
                y += ph
                if n == 0 and len(panels) > 1:
                    d.text((C.CX, y + 30), "≠", font=font(SANS["Bold"], 46), fill=P["muted"], anchor="mm")
                    y += 60
            if slide.get("summary"):
                sf = font(SANS["SemiBold"], 40 if tall else 35)
                y += 26
                seg_text(d, 0, y, slide["summary"], sf, P["accent"], P["accent"], anchor_center=C.CX)
        h = sum(p[4] for p in panels) + (60 if len(panels) > 1 else 0) + (80 if slide.get("summary") else 0)
        add(h, f_vs)

    # grid4: 2x2 개념 상자
    if kind == "grid4":
        cells = slide.get("cells", [])[:4]
        gap = 22
        cw = (maxw + 40 - gap) / 2
        hf = title_font("".join(c.get("head", "") for c in cells), 46 if tall else 40)
        tf2 = font(SANS["Regular"], 32 if tall else 28)
        texts = [wrap(d, c.get("text", ""), tf2, cw - 40) for c in cells]
        ch = max(len(t) for t in texts) * (42 if tall else 38) + (200 if tall else 180)

        def f_grid(y):
            for i, c in enumerate(cells):
                x = C.X0 - 20 + (i % 2) * (cw + gap)
                yy = y + (i // 2) * (ch + gap)
                fill = P["tint"] if i in (0, 3) else mix(P["card"], P["accent"], 0.08)
                d.rounded_rectangle((x, yy, x + cw, yy + ch), radius=30, fill=fill)
                icon(d, c.get("icon", "dot"), x + cw / 2, yy + 58, 30, P["accent"], fill)
                d.text((x + cw / 2, yy + 120), c.get("head", ""), font=hf, fill=P["ink"], anchor="mm")
                ty = yy + 160
                for wl in texts[i]:
                    d.text((x + cw / 2, ty), wl, font=tf2, fill=P["body"], anchor="ma")
                    ty += 42 if tall else 38
        add(2 * ch + gap + 30, f_grid)

    # rows3: 아이콘 + 굵은 한 줄 + 인용 + 설명
    if kind == "rows3":
        rws = slide.get("rows", [])
        hf = font(SANS["Bold"], 40 if tall else 35)
        qf = font(SANS["Regular"], 34 if tall else 30)
        rh = []
        wrapped = []
        for r in rws:
            q = wrap(d, r.get("quote", ""), qf, maxw - 150) if r.get("quote") else []
            t = wrap(d, r.get("text", ""), qf, maxw - 150) if r.get("text") else []
            wrapped.append((q, t))
            rh.append(36 + 52 + (len(q) + len(t)) * (46 if tall else 42) + 30)

        def f_rows(y):
            for r, (q, t), h in zip(rws, wrapped, rh):
                d.rounded_rectangle((C.X0 - 20, y, C.X1 + 20, y + h), radius=28, fill=P["tint"])
                d.ellipse((C.X0 + 6, y + 30, C.X0 + 86, y + 110), fill=P["card"])
                icon(d, r.get("icon", "dot"), C.X0 + 46, y + 70, 24, P["accent"], P["card"])
                x = C.X0 + 116
                d.text((x, y + 34), r.get("head", ""), font=hf, fill=P["ink"])
                ty = y + 36 + 52
                for wl in q:
                    d.text((x, ty), wl, font=qf, fill=P["accent"])
                    ty += 46 if tall else 42
                for wl in t:
                    d.text((x, ty), wl, font=qf, fill=P["body"])
                    ty += 46 if tall else 42
                y += h + 18
        add(sum(rh) + 18 * len(rh), f_rows)

    # 서비스 칩 (예약 카드)
    if slide.get("chips"):
        cf = font(SANS["SemiBold"], 32 if tall else 28)
        chips = slide["chips"]

        def layout(y=0, draw=False):
            x, rowh, yy = C.X0, 62, y
            lines = [[]]
            for c in chips:
                w = d.textlength(c, font=cf) + 48
                if sum(d.textlength(cc, font=cf) + 60 for cc in lines[-1]) + w > maxw:
                    lines.append([])
                lines[-1].append(c)
            for ln in lines:
                tw = sum(d.textlength(c, font=cf) + 48 for c in ln) + 12 * (len(ln) - 1)
                x = C.CX - tw / 2
                for c in ln:
                    w = d.textlength(c, font=cf) + 48
                    if draw:
                        d.rounded_rectangle((x, yy, x + w, yy + 52), radius=26, outline=P["accent"], width=2, fill=P["card"])
                        d.text((x + w / 2, yy + 26), c, font=cf, fill=P["accent"], anchor="mm")
                    x += w + 12
                yy += rowh
            return yy - y
        add(layout() + 20, lambda y: layout(y, True))

    for key, solid in (("outline_button", False), ("button", True)):
        if slide.get(key):
            bfnt = font(SANS["Bold"] if solid else SANS["SemiBold"], 40 if tall else 36)
            txt = slide[key]

            def f_btn(y, txt=txt, bfnt=bfnt, solid=solid):
                tw = d.textlength(txt, font=bfnt)
                bh = 96 if tall else 88
                x0 = C.CX - tw / 2 - 50
                if solid:
                    d.rounded_rectangle((x0, y, x0 + tw + 100, y + bh), radius=bh // 2, fill=P["accent"])
                    d.text((C.CX, y + bh / 2), txt, font=bfnt, fill=P["on_accent"], anchor="mm")
                else:
                    d.rounded_rectangle((x0, y, x0 + tw + 100, y + bh), radius=bh // 2, outline=P["accent"], width=3)
                    d.text((C.CX, y + bh / 2), txt, font=bfnt, fill=P["accent"], anchor="mm")
            add((96 if tall else 88) + 30, f_btn)

    # 세로 가운데 정렬 (표지는 살짝 위)
    total_h = sum(h for h, _ in blocks)
    avail = foot_y - content_top
    if total_h > avail:
        print(f"  ⚠️ 글이 넘칠 수 있음({total_h}>{avail}): {slide.get('title')}", file=sys.stderr)
    y = content_top + max(0, (avail - total_h) / (2.6 if kind == "cover" else 2))
    for h, fn in blocks:
        fn(y)
        y += h

    if band:
        bfnt = font(SANS["SemiBold"], 32 if tall else 28)
        bh = 70 if tall else 62
        by = H - C.m - (200 if tall else 112) - bh - 20
        d.rounded_rectangle((C.X0, by, C.X1, by + bh), radius=bh // 2, fill=P["accent"])
        d.text((C.CX, by + bh / 2), band, font=bfnt, fill=P["on_accent"], anchor="mm")

    if footer:
        fy = H - C.m - (190 if tall else 100)
        d.line((C.CX - 40, fy, C.CX + 40, fy), fill=P["accent"], width=3)
        d.text((C.CX, fy + 22), "마음길연구소 이지혜 소장", font=font(SANS["SemiBold"], 32 if tall else 28), fill=P["ink"], anchor="ma")
        d.text((C.CX, fy + 62), "한국심리분석협회 @k_paa_official", font=font(SANS["Regular"], 28 if tall else 24), fill=P["muted"], anchor="ma")
    return C.img
