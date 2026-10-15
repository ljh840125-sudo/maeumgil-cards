"""마음길연구소 카드뉴스 / 숏츠 생성기.

사용법: python3 render.py content/2026-10-19.json
결과: out/<post id>/card_01.png ... , out/<post id>/shorts.mp4
"""
import json
import os
import subprocess
import sys

from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.abspath(__file__))
FONT = os.path.join(ROOT, "fonts")
TITLE = os.path.join(FONT, "gowun-batang-korean-700-normal.woff")
SANS = {w: os.path.join(FONT, f"Pretendard-{w}.otf") for w in ("Regular", "SemiBold", "Bold", "ExtraBold")}

THEMES = {
    # 몽글몽글 포근한 톤: 크림 살구 배경 + 코코아 글씨 + 더스티 로즈 포인트
    "warm": {"bg": (250, 241, 233), "title": (78, 60, 66), "body": (112, 96, 100), "accent": (204, 128, 118), "muted": (160, 140, 136),
             "blobs": [((246, 212, 198), (0.85, 0.12, 0.38)), ((236, 222, 242), (0.08, 0.9, 0.42)), ((252, 228, 210), (0.95, 0.75, 0.25))]},
    "dark": {"bg": (27, 26, 46), "title": (255, 255, 255), "body": (204, 200, 222), "accent": (232, 190, 120), "muted": (150, 146, 172)},
    "light": {"bg": (246, 240, 230), "title": (40, 38, 62), "body": (88, 84, 104), "accent": (184, 136, 72), "muted": (140, 132, 120)},
}

BOOKING = {
    "type": "booking",
    "label": "마음길연구소",
    "title": ["혼자 풀기 어려운 마음,", "같이 들여다봐요"],
    "body": ["TCI 기질검사 해석 · 커플·연애 상담", "2,000여 명의 마음을 들어온 이지혜 소장이", "당신의 이야기를 기다리고 있어요."],
    "button": "프로필 링크 → 네이버 예약",
}

_font_cache = {}


def font(path, size):
    key = (path, size)
    if key not in _font_cache:
        _font_cache[key] = ImageFont.truetype(path, size)
    return _font_cache[key]


def wrap(draw, text, fnt, max_w):
    """한국어 문장을 픽셀 폭에 맞춰 줄바꿈 (공백 우선, 넘치면 글자 단위)."""
    lines, cur = [], ""
    for word in text.split(" "):
        trial = (cur + " " + word).strip()
        if draw.textlength(trial, font=fnt) <= max_w:
            cur = trial
            continue
        if cur:
            lines.append(cur)
        cur = ""
        for ch in word:
            if draw.textlength(cur + ch, font=fnt) > max_w:
                lines.append(cur)
                cur = ch
            else:
                cur += ch
    if cur:
        lines.append(cur)
    return lines


def draw_art(img, kind, th, box):
    """금요일 '마음 한 장'용 간단한 일러스트 (4배 크기로 그린 뒤 축소해 부드럽게)."""
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    S = 4
    layer = Image.new("RGBA", (w * S, h * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    acc = th["accent"] + (255,)
    soft = th["accent"] + (70,)
    cx, cy = w * S // 2, h * S // 2
    if kind == "moon":
        r = min(w, h) * S // 3
        off = int(r * 0.55)
        mask = Image.new("L", layer.size, 0)
        md = ImageDraw.Draw(mask)
        md.ellipse((cx - r, cy - r, cx + r, cy + r), fill=255)
        md.ellipse((cx - r + off, cy - r - off // 3, cx + r + off, cy + r - off // 3), fill=0)
        layer.paste(Image.new("RGBA", layer.size, acc), (0, 0), mask)
        for sx, sy, sr in [(0.15, 0.25, 10), (0.82, 0.2, 14), (0.75, 0.78, 9), (0.22, 0.8, 12), (0.9, 0.5, 7)]:
            px, py, pr = int(w * S * sx), int(h * S * sy), sr * S // 2
            d.ellipse((px - pr, py - pr, px + pr, py + pr), fill=soft)
    elif kind == "path":
        pts = []
        for i in range(0, 101):
            t = i / 100
            px = int(w * S * (0.08 + 0.84 * t))
            py = int(h * S * (0.85 - 0.6 * t + 0.18 * __import__("math").sin(t * 6.3)))
            pts.append((px, py))
        d.line(pts, fill=soft, width=10 * S, joint="curve")
        for i in range(0, 101, 12):
            px, py = pts[i]
            r = 9 * S
            d.ellipse((px - r, py - r, px + r, py + r), fill=acc)
        px, py = pts[-1]
        r = 22 * S
        d.ellipse((px - r, py - r, px + r, py + r), fill=acc)
    layer = layer.resize((w, h), Image.LANCZOS)
    img.paste(layer, (x0, y0), layer)


def render_slide(slide, th, W, H, page=None, total=None, footer=True):
    img = Image.new("RGB", (W, H), th["bg"])
    if th.get("blobs"):
        from PIL import ImageFilter
        layer = Image.new("RGB", (W, H), th["bg"])
        ld = ImageDraw.Draw(layer)
        for col, (bx, by, br) in th["blobs"]:
            r = int(W * br)
            cx, cy = int(W * bx), int(H * by)
            ld.ellipse((cx - r, cy - r, cx + r, cy + r), fill=col)
        img = layer.filter(ImageFilter.GaussianBlur(90))
    d = ImageDraw.Draw(img)
    M = 90
    max_w = W - 2 * M
    tall = H > 1500
    top = 300 if tall else 120

    if slide.get("label"):
        d.text((M, top), slide["label"], font=font(SANS["SemiBold"], 44 if tall else 38), fill=th["accent"])
    if page and total:
        d.text((W - M, top), f"{page}/{total}", font=font(SANS["Regular"], 32), fill=th["muted"], anchor="ra")

    kind = slide["type"]
    y = top + (220 if tall else 200)

    if kind == "quote" and slide.get("art"):
        art_h = 360 if not tall else 460
        draw_art(img, slide["art"], th, (M, y - 40, W - M, y - 40 + art_h))
        y += art_h

    title_size = 88 if kind == "cover" else 72
    if kind == "quote":
        title_size = 70
    if kind == "profile":
        title_size = 80
    tf = font(TITLE, title_size)
    for line in slide.get("title", []):
        for wl in wrap(d, line, tf, max_w):
            d.text((M, y), wl, font=tf, fill=th["title"])
            y += int(title_size * 1.42)
    y += 50

    bf = font(SANS["Regular"], 44 if tall else 40)
    lh = 72 if tall else 66
    for line in slide.get("sub", []) + slide.get("body", []):
        for wl in wrap(d, line, bf, max_w):
            d.text((M, y), wl, font=bf, fill=th["body"])
            y += lh

    if slide.get("items"):
        y += 10
        bullet_f = font(SANS["Regular"], 42 if tall else 38)
        for it in slide["items"]:
            wl = wrap(d, it, bullet_f, max_w - 50)
            r = 7
            d.ellipse((M, y + 24 - r, M + 2 * r, y + 24 + r), fill=th["accent"])
            for k, ln in enumerate(wl):
                d.text((M + 44, y), ln, font=bullet_f, fill=th["body"])
                y += 62
            y += 22

    if slide.get("button"):
        y += 40
        bfnt = font(SANS["Bold"], 42 if tall else 38)
        tw = d.textlength(slide["button"], font=bfnt)
        bh = 100 if tall else 92
        d.rounded_rectangle((M, y, M + tw + 100, y + bh), radius=bh // 2, fill=th["accent"])
        d.text((M + 50, y + bh // 2), slide["button"], font=bfnt, fill=(255, 255, 255), anchor="lm")
        y += bh

    if footer:
        fy = H - (360 if tall else 170)
        d.line((M, fy, W - M, fy), fill=th["accent"], width=2)
        d.text((M, fy + 30), "마음길연구소 이지혜 소장", font=font(SANS["SemiBold"], 34 if tall else 30), fill=th["title"])
        d.text((M, fy + 80), "한국심리분석협회 @k_paa_official", font=font(SANS["Regular"], 30 if tall else 26), fill=th["muted"])

    if y > H - (380 if tall else 190):
        print(f"  ⚠️ 글이 하단 영역과 겹칠 수 있음: {slide.get('title')}", file=sys.stderr)
    return img


def make_shorts(frames_dir, frames, out_path):
    """장면마다 글자 수에 맞춰 시간을 주고 페이드로 연결."""
    durs = []
    for f, txt in frames:
        durs.append(max(3.5, min(6.5, 2.0 + len(txt) / 18)))
    args = ["ffmpeg", "-y", "-loglevel", "error"]
    for (f, _), t in zip(frames, durs):
        args += ["-loop", "1", "-t", f"{t:.2f}", "-i", f]
    fade = 0.6
    if len(frames) == 1:
        filt = "[0]format=yuv420p[v]"
    else:
        parts, prev, offset = [], "[0]", 0.0
        for i in range(1, len(frames)):
            offset += durs[i - 1] - fade
            out = f"[x{i}]" if i < len(frames) - 1 else "[xv]"
            parts.append(f"{prev}[{i}]xfade=transition=fade:duration={fade}:offset={offset:.2f}{out}")
            prev = out
        filt = ";".join(parts) + ";[xv]format=yuv420p[v]"
    args += ["-filter_complex", filt, "-map", "[v]", "-r", "30", "-c:v", "libx264",
             "-profile:v", "high", "-crf", "20", "-movflags", "+faststart", out_path]
    subprocess.run(args, check=True)


def slide_text(s):
    return " ".join(s.get("title", []) + s.get("sub", []) + s.get("body", []) + s.get("items", []))


def render_post(post, out_root):
    th = THEMES[post.get("theme", "warm")]
    out = os.path.join(out_root, post["id"])
    os.makedirs(out, exist_ok=True)
    slides = list(post["slides"])
    booking = dict(BOOKING, **post.get("booking", {}))
    slides.append(booking)
    total = len(slides)
    files = []
    for i, s in enumerate(slides, 1):
        img = render_slide(s, th, 1080, 1350, page=i if total > 1 else None, total=total if total > 1 else None)
        p = os.path.join(out, f"card_{i:02d}.png")
        img.save(p, optimize=True)
        files.append(p)

    frames = []
    for i, s in enumerate([s for s in post["slides"] if s.get("shorts")], 1):
        img = render_slide(s, th, 1080, 1920)
        p = os.path.join(out, f"frame_{i:02d}.png")
        img.save(p)
        frames.append((p, slide_text(s)))
    end = render_slide(booking, th, 1080, 1920)
    endp = os.path.join(out, f"frame_{len(frames) + 1:02d}.png")
    end.save(endp)
    frames.append((endp, slide_text(booking)))
    make_shorts(out, frames, os.path.join(out, "shorts.mp4"))
    for p, _ in frames:
        os.remove(p)
    return files


def main():
    src = sys.argv[1]
    data = json.load(open(src, encoding="utf-8"))
    out_root = os.path.join(ROOT, "out")
    for post in data["posts"]:
        print(f"▶ {post['id']} ({post['series']})")
        render_post(post, out_root)
    print("done")


if __name__ == "__main__":
    main()
