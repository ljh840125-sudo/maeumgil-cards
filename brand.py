"""마음길연구소 브랜드 키트 v2 — '길라잡이' 엠블럼.

엠블럼: 아치(마음의 문) 안으로 굽이진 길이 이어지고, 그 위에 북극성(길잡이 별)이 빛난다.
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
DUSK_TOP = (176, 156, 204)     # 해 질 녘 위쪽 (연보라)
DUSK_MID = (226, 178, 192)     # 장밋빛
DUSK_BOT = (248, 208, 182)     # 살구빛 지평선
STAR = (255, 246, 226)
TAGLINE = "길을 잃은 마음에, 길잡이가 되어드릴게요"

TAGLINE_SHORT = "마음의 길잡이"


def f(path, size):
    return ImageFont.truetype(path, size)


def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def gradient(w, h, stops):
    img = Image.new("RGB", (w, h))
    d = ImageDraw.Draw(img)
    for y in range(h):
        t = y / max(1, h - 1)
        for i in range(len(stops) - 1):
            t0, c0 = stops[i]
            t1, c1 = stops[i + 1]
            if t0 <= t <= t1:
                d.line([(0, y), (w, y)], fill=lerp(c0, c1, (t - t0) / max(1e-6, t1 - t0)))
                break
    return img


def soft_bg(w, h, blobs=None, blur=None):
    blobs = blobs or [(PEACH, 0.88, 0.1, 0.42), (LILAC, 0.06, 0.92, 0.45), (APRICOT, 0.96, 0.8, 0.28)]
    img = Image.new("RGB", (w, h), BG)
    d = ImageDraw.Draw(img)
    base = max(w, h)
    for col, bx, by, br in blobs:
        r = int(base * br)
        cx, cy = int(w * bx), int(h * by)
        d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=col)
    return img.filter(ImageFilter.GaussianBlur(blur or base // 12))


def star_points(cx, cy, r_out, r_in, n=4, rot=-math.pi / 2):
    pts = []
    for i in range(n * 2):
        r = r_out if i % 2 == 0 else r_in
        a = rot + i * math.pi / n
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts


def emblem(size):
    """아치 + 굽은 길 + 발걸음 + 북극성. RGBA, 정사각형 size x size."""
    S = 4
    W = H = size * S
    aw, ah = int(W * 0.70), int(H * 0.90)
    ax, ay = (W - aw) // 2, (H - ah) // 2
    # 아치 마스크
    mask = Image.new("L", (W, H), 0)
    md = ImageDraw.Draw(mask)
    md.ellipse((ax, ay, ax + aw, ay + aw), fill=255)
    md.rectangle((ax, ay + aw // 2, ax + aw, ay + ah), fill=255)
    # 하늘 그라데이션
    sky = gradient(W, H, [(0.0, DUSK_TOP), (0.55, DUSK_MID), (0.72, DUSK_BOT), (1.0, DUSK_BOT)])
    scene = sky.convert("RGBA")
    d = ImageDraw.Draw(scene)
    horizon = ay + int(ah * 0.62)
    # 겹겹이 언덕
    for k, (col, amp, off) in enumerate([((214, 170, 186), 0.05, 0.0), ((236, 196, 186), 0.04, 1.7)]):
        pts = [(ax, ay + ah)]
        for i in range(61):
            x = ax + aw * i / 60
            y = horizon + int(ah * 0.03 * k) - int(ah * amp * (0.5 + 0.5 * math.sin(i / 60 * 5.5 + off)))
            pts.append((x, y))
        pts.append((ax + aw, ay + ah))
        d.polygon(pts, fill=col + (255,))
    # 굽이진 길 (아래는 넓고 위로 갈수록 좁아짐)
    left, right, center = [], [], []
    N = 80
    for i in range(N + 1):
        t = i / N  # 0=아래, 1=지평선
        y = ay + ah - (ay + ah - horizon - int(ah * 0.02)) * t
        cx = W / 2 + aw * 0.16 * math.sin(t * math.pi * 1.6 + 0.4) * (1 - t * 0.6)
        half = aw * (0.20 * (1 - t) ** 1.3 + 0.008)
        left.append((cx - half, y))
        right.append((cx + half, y))
        center.append((cx, y))
    d.polygon(left + right[::-1], fill=BG + (255,))
    # 발걸음 점
    for i in (8, 20, 32, 43, 53, 62, 70):
        x, y = center[i]
        t = i / N
        r = aw * 0.022 * (1 - t * 0.75)
        d.ellipse((x - r, y - r, x + r, y + r), fill=ROSE + (255,))
    # 북극성 빛 번짐
    sx, sy = W / 2, ay + int(ah * 0.24)
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    for rr, a in [(aw * 0.30, 50), (aw * 0.19, 80), (aw * 0.11, 120)]:
        gd.ellipse((sx - rr, sy - rr, sx + rr, sy + rr), fill=(255, 238, 214, a))
    glow = glow.filter(ImageFilter.GaussianBlur(aw * 0.05))
    scene = Image.alpha_composite(scene, glow)
    d = ImageDraw.Draw(scene)
    d.polygon(star_points(sx, sy, aw * 0.13, aw * 0.032), fill=STAR + (255,))
    d.polygon(star_points(sx, sy, aw * 0.07, aw * 0.02, rot=-math.pi / 4), fill=STAR + (255,))
    # 작은 별
    for px, py, pr in [(0.30, 0.16, 0.012), (0.72, 0.13, 0.009), (0.78, 0.36, 0.011), (0.25, 0.40, 0.008), (0.62, 0.30, 0.006)]:
        x, y, r = ax + aw * px, ay + ah * py, aw * pr
        d.ellipse((x - r, y - r, x + r, y + r), fill=STAR + (230,))
    out = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    out.paste(scene, (0, 0), mask)
    # 아치 테두리
    od = ImageDraw.Draw(out)
    lw = max(2, int(aw * 0.012))
    od.arc((ax, ay, ax + aw, ay + aw), 180, 360, fill=ROSE + (255,), width=lw)
    od.line([(ax + lw // 2, ay + aw // 2), (ax + lw // 2, ay + ah)], fill=ROSE + (255,), width=lw)
    od.line([(ax + aw - lw // 2, ay + aw // 2), (ax + aw - lw // 2, ay + ah)], fill=ROSE + (255,), width=lw)
    od.line([(ax, ay + ah - lw // 2), (ax + aw, ay + ah - lw // 2)], fill=ROSE + (255,), width=lw)
    return out.resize((size, size), Image.LANCZOS)


def paste_emblem(img, cx, cy, size):
    e = emblem(size)
    img.paste(e, (int(cx - size / 2), int(cy - size / 2)), e)


def ctext(d, xy, text, font, fill):
    d.text(xy, text, font=font, fill=fill, anchor="mm")


# ---------- 1) 프로필 (인스타·쓰레드·유튜브·블로그 공통) ----------
def profile():
    W = 1080
    img = soft_bg(W, W, [(PEACH, 0.85, 0.15, 0.45), (LILAC, 0.1, 0.9, 0.45)])
    paste_emblem(img, W // 2, int(W * 0.41), 640)
    d = ImageDraw.Draw(img)
    ctext(d, (W // 2, int(W * 0.80)), "마음길", f(SERIF_B, 120), COCOA)
    img.save(os.path.join(OUT, "01_profile_1080.png"))
    img.resize((400, 400), Image.LANCZOS).save(os.path.join(OUT, "01_profile_400.png"))
    small = img.resize((400, 400), Image.LANCZOS)
    m = Image.new("L", (400, 400), 0)
    ImageDraw.Draw(m).ellipse((0, 0, 400, 400), fill=255)
    prev = Image.new("RGB", (440, 440), (255, 255, 255))
    prev.paste(small, (20, 20), m)
    prev.save(os.path.join(OUT, "_preview_profile_circle.png"))


# ---------- 2) 유튜브 배너 ----------
def youtube():
    W, H = 2560, 1440
    img = soft_bg(W, H, [(PEACH, 0.82, 0.3, 0.3), (LILAC, 0.15, 0.7, 0.3), (APRICOT, 0.6, 0.75, 0.18)], blur=160)
    d = ImageDraw.Draw(img)
    sx0, sy0 = (W - 1546) // 2, (H - 423) // 2
    paste_emblem(img, sx0 + 190, H // 2, 420)
    tx = sx0 + 420
    d.text((tx, sy0 + 30), "마음길연구소", font=f(SERIF_B, 118), fill=COCOA)
    d.text((tx, sy0 + 190), TAGLINE, font=f(SERIF_R, 58), fill=BODY)
    d.text((tx, sy0 + 300), "TCI 기질 이야기 · 커플 궁합 · 관계 심리  |  매일 밤 9시", font=f(SANS["SemiBold"], 40), fill=ROSE)
    img.save(os.path.join(OUT, "02_youtube_banner_2560x1440.png"))
    pv = img.copy()
    ImageDraw.Draw(pv).rectangle((sx0, sy0, sx0 + 1546, sy0 + 423), outline=(120, 120, 200), width=6)
    pv.resize((1280, 720)).save(os.path.join(OUT, "_preview_youtube_safezone.png"))


# ---------- 3) 인스타 하이라이트 커버 ----------
def icon(kind, size):
    S = 4
    w = size * S
    im = Image.new("RGBA", (w, w), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    c = COCOA + (255,)
    lw = int(w * 0.045)
    m = w / 2
    if kind == "star":       # 기질 해부실: 북극성
        d.polygon(star_points(m, m, w * 0.4, w * 0.1), fill=c)
    elif kind == "rings":    # 궁합 연구소: 겹친 두 원
        r = w * 0.26
        d.ellipse((m - r * 1.55, m - r, m + r * 0.45, m + r), outline=c, width=lw)
        d.ellipse((m - r * 0.45, m - r, m + r * 1.55, m + r), outline=ROSE + (255,), width=lw)
    elif kind == "book":     # 검사 도감: 펼친 책
        d.line([(m, w * 0.28), (m, w * 0.76)], fill=c, width=lw)
        d.line([(w * 0.14, w * 0.3), (m, w * 0.36), (w * 0.86, w * 0.3)], fill=c, width=lw, joint="curve")
        d.line([(w * 0.14, w * 0.3), (w * 0.14, w * 0.7), (m, w * 0.76), (w * 0.86, w * 0.7), (w * 0.86, w * 0.3)], fill=c, width=lw, joint="curve")
    elif kind == "check":    # 셀프 체크
        d.rounded_rectangle((w * 0.18, w * 0.18, w * 0.82, w * 0.82), radius=w * 0.12, outline=c, width=lw)
        d.line([(w * 0.32, w * 0.5), (w * 0.45, w * 0.64), (w * 0.7, w * 0.36)], fill=ROSE + (255,), width=int(lw * 1.3), joint="curve")
    return im.resize((size, size), Image.LANCZOS)


HIGHLIGHTS = [("star", "기질 해부실"), ("rings", "궁합 연구소"), ("book", "검사 도감"), ("check", "셀프 체크"), ("emblem", "상담 예약")]


def highlights():
    W, H = 1080, 1920
    sheet = Image.new("RGB", (5 * 230 + 30, 300), (255, 255, 255))
    sd = ImageDraw.Draw(sheet)
    for i, (k, name) in enumerate(HIGHLIGHTS):
        img = soft_bg(W, H, [(PEACH, 0.5, 0.42, 0.33), (LILAC, 0.5, 0.6, 0.3)], blur=120)
        if k == "emblem":
            paste_emblem(img, W // 2, H // 2, 560)
        else:
            ic = icon(k, 360)
            img.paste(ic, (W // 2 - 180, H // 2 - 180), ic)
        img.save(os.path.join(OUT, f"03_highlight_{i + 1}_{name.replace(' ', '')}.png"))
        crop = img.crop((0, (H - W) // 2, W, (H + W) // 2)).resize((200, 200), Image.LANCZOS)
        m = Image.new("L", (200, 200), 0)
        ImageDraw.Draw(m).ellipse((0, 0, 200, 200), fill=255)
        sheet.paste(crop, (30 + i * 230, 30), m)
        sd.text((130 + i * 230, 260), name, font=f(SANS["Regular"], 22), fill=COCOA, anchor="mm")
    sheet.save(os.path.join(OUT, "_preview_highlights.png"))


# ---------- 4) 네이버 블로그 ----------
def blog_title():
    W, H = 966, 400
    img = soft_bg(W, H, [(PEACH, 0.9, 0.2, 0.32), (LILAC, 0.05, 0.95, 0.3), (APRICOT, 0.55, 1.0, 0.2)], blur=70)
    d = ImageDraw.Draw(img)
    paste_emblem(img, 175, H // 2, 330)
    d.text((330, 96), "마음길연구소", font=f(SERIF_B, 66), fill=COCOA)
    d.text((332, 190), TAGLINE, font=f(SERIF_R, 30), fill=BODY)
    d.text((332, 248), "이지혜 소장  ·  TCI 기질검사  ·  커플·관계·중독 상담", font=f(SANS["SemiBold"], 21), fill=ROSE)
    d.line([(332, 300), (900, 300)], fill=ROSE, width=1)
    d.text((332, 316), "2,000여 명의 마음을 들어온 상담가가, 당신의 마음길을 함께 걷습니다.", font=f(SANS["Regular"], 18), fill=MUTED)
    img.save(os.path.join(OUT, "04_blog_title_966x400.png"))
    return img


def blog_mobile():
    W, H = 1600, 900
    m = soft_bg(W, H, [(PEACH, 0.85, 0.2, 0.32), (LILAC, 0.1, 0.85, 0.32)], blur=110)
    md = ImageDraw.Draw(m)
    paste_emblem(m, W // 2, 320, 460)
    ctext(md, (W // 2, 620), "마음길연구소", f(SERIF_B, 100), COCOA)
    ctext(md, (W // 2, 730), TAGLINE, f(SERIF_R, 48), BODY)
    m.save(os.path.join(OUT, "05_blog_mobile_cover_1600x900.png"))


def widgets():
    """네이버 블로그 사이드 위젯 (가로 170px 규격, 2배 해상도로 제작)."""
    items = [
        ("06_widget_booking", "상담 예약", "네이버 예약 바로가기", True),
        ("07_widget_tci", "TCI 기질검사", "검사 안내 · 해석 상담", False),
        ("08_widget_couple", "커플·관계 상담", "두 사람의 기질 궁합", False),
    ]
    outs = []
    for name, title, sub, primary in items:
        W, H = 340, 200
        img = soft_bg(W, H, [(PEACH, 0.9, 0.1, 0.6), (LILAC, 0.0, 1.0, 0.6)], blur=40)
        d = ImageDraw.Draw(img)
        if primary:
            d.rounded_rectangle((14, 14, W - 14, H - 14), radius=28, fill=ROSE)
            ctext(d, (W // 2, 82), title, f(SERIF_B, 46), (255, 255, 255))
            ctext(d, (W // 2, 140), sub + "  →", f(SANS["SemiBold"], 22), (255, 240, 236))
        else:
            d.rounded_rectangle((14, 14, W - 14, H - 14), radius=28, outline=ROSE, width=3)
            ic = emblem(70)
            img.paste(ic, (W // 2 - 35, 22), ic)
            ctext(d, (W // 2, 118), title, f(SERIF_B, 36), COCOA)
            ctext(d, (W // 2, 160), sub, f(SANS["Regular"], 20), BODY)
        img.save(os.path.join(OUT, name + "_170x100@2x.png"))
        outs.append(img)
    return outs


def blog_mockup(title_img, widget_imgs):
    """블로그 메인 화면 구성 미리보기 (실제 배치 예시)."""
    W, H = 1200, 1260
    pg = Image.new("RGB", (W, H), (255, 255, 255))
    d = ImageDraw.Draw(pg)
    d.rectangle((0, 0, W, 54), fill=(245, 245, 245))
    d.text((24, 16), "blog.naver.com", font=f(SANS["Regular"], 20), fill=(150, 150, 150))
    x0 = (W - 966) // 2
    pg.paste(title_img, (x0, 70))
    # 메뉴
    menu_y = 70 + 400 + 14
    d.rectangle((x0, menu_y, x0 + 966, menu_y + 46), fill=BG)
    for i, mtxt in enumerate(["전체글", "기질 해부실", "궁합 연구소", "검사 도감", "마음 한 장", "상담 안내"]):
        d.text((x0 + 26 + i * 150, menu_y + 12), mtxt, font=f(SANS["SemiBold"], 19), fill=COCOA if i else ROSE)
    # 왼쪽 사이드
    sy = menu_y + 70
    prof = Image.open(os.path.join(OUT, "01_profile_400.png")).resize((150, 150))
    pm = Image.new("L", (150, 150), 0)
    ImageDraw.Draw(pm).ellipse((0, 0, 150, 150), fill=255)
    pg.paste(prof, (x0 + 10, sy), pm)
    d.text((x0 + 10, sy + 165), "이지혜 소장", font=f(SERIF_B, 24), fill=COCOA)
    d.text((x0 + 10, sy + 198), "마음의 길잡이", font=f(SANS["Regular"], 17), fill=MUTED)
    wy = sy + 240
    for wimg in widget_imgs:
        pg.paste(wimg.resize((170, 100), Image.LANCZOS), (x0, wy))
        wy += 112
    # 본문: 최신 카드뉴스 썸네일
    bx = x0 + 210
    d.text((bx, sy), "최근 글", font=f(SERIF_B, 26), fill=COCOA)
    thumbs = ["2026-10-19-mon", "2026-10-20-tue", "2026-10-21-wed", "2026-10-22-thu", "2026-10-23-fri", "2026-10-16-fri"]
    for i, t in enumerate(thumbs):
        p = os.path.join(ROOT, "out", t, "card_01.png")
        if not os.path.exists(p):
            continue
        th = Image.open(p).resize((236, 295), Image.LANCZOS)
        cx = bx + (i % 3) * 252
        cy = sy + 46 + (i // 3) * 310
        pg.paste(th, (cx, cy))
    d.text((W // 2, H - 24), "※ 배치 예시 화면입니다", font=f(SANS["Regular"], 16), fill=(170, 170, 170), anchor="mm")
    pg.save(os.path.join(OUT, "_preview_blog_main.png"))


def emblem_sheet():
    """디자인 의미 설명용 엠블럼 단독 이미지."""
    W = 900
    img = Image.new("RGB", (W, W), BG)
    paste_emblem(img, W // 2, W // 2, 760)
    img.save(os.path.join(OUT, "00_emblem_900.png"))


if __name__ == "__main__":
    for fn in os.listdir(OUT):
        if fn.endswith(".png"):
            os.remove(os.path.join(OUT, fn))
    emblem_sheet()
    profile()
    youtube()
    highlights()
    t = blog_title()
    blog_mobile()
    w = widgets()
    blog_mockup(t, w)
    print("done:", sorted(os.listdir(OUT)))
