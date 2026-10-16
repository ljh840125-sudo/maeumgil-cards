"""마음길연구소 브랜드 키트 생성기 (카드뉴스와 같은 색·글꼴·모티프).

사용법: python3 brand.py  → brand/ 폴더에 PNG 생성
"""
import math
import os

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = os.path.dirname(os.path.abspath(__file__))
F = os.path.join(ROOT, "fonts")
SERIF_B = os.path.join(F, "gowun-batang-korean-700-normal.woff")
SERIF_R = os.path.join(F, "gowun-batang-korean-400-normal.woff")
SANS = {w: os.path.join(F, f"Pretendard-{w}.otf") for w in ("Regular", "SemiBold", "Bold")}
OUT = os.path.join(ROOT, "brand")
os.makedirs(OUT, exist_ok=True)

BG = (250, 241, 233)
COCOA = (78, 60, 66)
BODY = (112, 96, 100)
ROSE = (204, 128, 118)
MUTED = (160, 140, 136)
PEACH = (246, 212, 198)
LILAC = (236, 222, 242)
APRICOT = (252, 228, 210)


def f(path, size):
    return ImageFont.truetype(path, size)


def soft_bg(w, h, blobs=None, blur=None):
    """카드뉴스와 같은 몽글몽글 번짐 배경."""
    blobs = blobs or [(PEACH, 0.88, 0.1, 0.42), (LILAC, 0.06, 0.92, 0.45), (APRICOT, 0.96, 0.8, 0.28)]
    img = Image.new("RGB", (w, h), BG)
    d = ImageDraw.Draw(img)
    base = max(w, h)
    for col, bx, by, br in blobs:
        r = int(base * br)
        cx, cy = int(w * bx), int(h * by)
        d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=col)
    return img.filter(ImageFilter.GaussianBlur(blur or base // 12))


def draw_mark(img, cx, cy, size, color=ROSE, line_alpha=90):
    """로고 마크: 아래에서 위로 이어지는 길(점) 끝에 초승달."""
    S = 4
    w = h = size * S
    layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    pts = []
    for i in range(101):
        t = i / 100
        x = w * (0.14 + 0.5 * t)
        y = h * (0.86 - 0.52 * t + 0.07 * math.sin(t * 6.3))
        pts.append((x, y))
    d.line(pts, fill=color + (line_alpha,), width=int(size * 0.045 * S), joint="curve")
    for i in range(0, 76, 15):
        x, y = pts[i]
        r = size * 0.032 * S
        d.ellipse((x - r, y - r, x + r, y + r), fill=color + (255,))
    # 초승달
    mcx, mcy, mr = w * 0.7, h * 0.3, size * 0.2 * S
    mask = Image.new("L", (w, h), 0)
    md = ImageDraw.Draw(mask)
    md.ellipse((mcx - mr, mcy - mr, mcx + mr, mcy + mr), fill=255)
    off = mr * 0.55
    md.ellipse((mcx - mr + off, mcy - mr - off / 3, mcx + mr + off, mcy + mr - off / 3), fill=0)
    layer.paste(Image.new("RGBA", (w, h), color + (255,)), (0, 0), mask)
    layer = layer.resize((size, size), Image.LANCZOS)
    img.paste(layer, (int(cx - size / 2), int(cy - size / 2)), layer)


def center_text(d, xy, text, font, fill):
    d.text(xy, text, font=font, fill=fill, anchor="mm")


# 1) 프로필 사진 (인스타·쓰레드·유튜브·블로그 공통, 원형으로 잘려도 안전)
def profile():
    W = 1080
    img = soft_bg(W, W, [(PEACH, 0.85, 0.15, 0.45), (LILAC, 0.1, 0.9, 0.45)])
    draw_mark(img, W // 2 - 50, int(W * 0.42), 520)
    d = ImageDraw.Draw(img)
    center_text(d, (W // 2, int(W * 0.74)), "마음길", f(SERIF_B, 150), COCOA)
    img.save(os.path.join(OUT, "01_profile_1080.png"))
    img.resize((400, 400), Image.LANCZOS).save(os.path.join(OUT, "01_profile_400.png"))
    # 원형 미리보기
    prev = img.resize((400, 400), Image.LANCZOS)
    m = Image.new("L", (400, 400), 0)
    ImageDraw.Draw(m).ellipse((0, 0, 400, 400), fill=255)
    circ = Image.new("RGB", (440, 440), (255, 255, 255))
    circ.paste(prev, (20, 20), m)
    circ.save(os.path.join(OUT, "_preview_profile_circle.png"))


# 2) 유튜브 채널 배너 2560x1440 (모든 기기 안전영역 1546x423 안에 핵심)
def youtube():
    W, H = 2560, 1440
    img = soft_bg(W, H, [(PEACH, 0.82, 0.3, 0.3), (LILAC, 0.15, 0.7, 0.3), (APRICOT, 0.6, 0.75, 0.18)], blur=160)
    d = ImageDraw.Draw(img)
    sx0, sy0 = (W - 1546) // 2, (H - 423) // 2
    draw_mark(img, sx0 + 170, H // 2, 330)
    tx = sx0 + 380
    d.text((tx, sy0 + 40), "마음길연구소", font=f(SERIF_B, 118), fill=COCOA)
    d.text((tx, sy0 + 200), "기질을 알면, 마음이 덜 아파요", font=f(SERIF_R, 62), fill=BODY)
    d.text((tx, sy0 + 310), "TCI 기질 이야기 · 커플 궁합 · 관계 심리  |  매일 밤 9시", font=f(SANS["SemiBold"], 40), fill=ROSE)
    img.save(os.path.join(OUT, "02_youtube_banner_2560x1440.png"))
    # 안전영역 표시 미리보기
    pv = img.copy()
    ImageDraw.Draw(pv).rectangle((sx0, sy0, sx0 + 1546, sy0 + 423), outline=(120, 120, 200), width=6)
    pv.resize((1280, 720)).save(os.path.join(OUT, "_preview_youtube_safezone.png"))


# 3) 인스타 하이라이트 커버 (1080x1920, 가운데 원 안에 핵심)
HIGHLIGHTS = [
    ("기질", "해부실"),
    ("궁합", "연구소"),
    ("검사", "도감"),
    ("셀프", "체크"),
    ("상담", "예약"),
]


def highlights():
    W, H = 1080, 1920
    sheet = Image.new("RGB", (5 * 230 + 30, 260), (255, 255, 255))
    for i, (a, b) in enumerate(HIGHLIGHTS):
        img = soft_bg(W, H, [(PEACH, 0.5, 0.45, 0.35), (LILAC, 0.5, 0.58, 0.3)], blur=120)
        d = ImageDraw.Draw(img)
        if a == "상담":
            draw_mark(img, W // 2, H // 2 - 120, 300)
            center_text(d, (W // 2, H // 2 + 130), "상담 예약", f(SERIF_B, 120), COCOA)
        else:
            center_text(d, (W // 2, H // 2 - 80), a, f(SERIF_B, 170), COCOA)
            center_text(d, (W // 2, H // 2 + 110), b, f(SERIF_R, 110), ROSE)
        p = os.path.join(OUT, f"03_highlight_{i + 1}_{a}{b}.png")
        img.save(p)
        crop = img.crop((0, (H - W) // 2, W, (H + W) // 2)).resize((200, 200), Image.LANCZOS)
        m = Image.new("L", (200, 200), 0)
        ImageDraw.Draw(m).ellipse((0, 0, 200, 200), fill=255)
        sheet.paste(crop, (30 + i * 230, 30), m)
    sheet.save(os.path.join(OUT, "_preview_highlights.png"))


# 4) 네이버 블로그 상단 타이틀 이미지 (가로 966, 세로 50~600)
def blog():
    W, H = 966, 360
    img = soft_bg(W, H, [(PEACH, 0.9, 0.2, 0.32), (LILAC, 0.05, 0.95, 0.3), (APRICOT, 0.55, 1.0, 0.2)], blur=70)
    d = ImageDraw.Draw(img)
    draw_mark(img, 150, H // 2, 210)
    d.text((290, 92), "마음길연구소", font=f(SERIF_B, 64), fill=COCOA)
    d.text((292, 182), "기질을 알면, 마음이 덜 아파요", font=f(SERIF_R, 34), fill=BODY)
    d.text((292, 240), "이지혜 소장 · TCI 기질검사 · 커플·관계·중독 상담", font=f(SANS["SemiBold"], 22), fill=ROSE)
    img.save(os.path.join(OUT, "04_blog_title_966x360.png"))
    # 모바일 블로그 커버 (가로형 1600x900, 가운데 정렬)
    W2, H2 = 1600, 900
    m = soft_bg(W2, H2, [(PEACH, 0.85, 0.2, 0.32), (LILAC, 0.1, 0.85, 0.32)], blur=110)
    md = ImageDraw.Draw(m)
    draw_mark(m, W2 // 2, 300, 300)
    center_text(md, (W2 // 2, 540), "마음길연구소", f(SERIF_B, 110), COCOA)
    center_text(md, (W2 // 2, 660), "기질을 알면, 마음이 덜 아파요", f(SERIF_R, 52), BODY)
    m.save(os.path.join(OUT, "05_blog_mobile_cover_1600x900.png"))


if __name__ == "__main__":
    profile()
    youtube()
    highlights()
    blog()
    print("done:", sorted(os.listdir(OUT)))
