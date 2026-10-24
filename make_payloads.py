"""주간 JSON → Metricool 예약 payload 목록 출력.

사용법: python3 make_payloads.py content/<주시작일>.json <커밋SHA>
각 줄: === <post id> <IG|REEL|YT> <ISO 날짜시간+09:00>  다음 줄에 info JSON
"""
import datetime
import glob
import json
import sys

src, sha = sys.argv[1], sys.argv[2]
B = f"https://raw.githubusercontent.com/ljh840125-sudo/maeumgil-cards/{sha}/"
d = json.load(open(src, encoding="utf-8"))


def base(dt, text, media, prov, extra, first_comment=""):
    x = {"autoPublish": True, "draft": False, "descendants": [], "firstCommentText": first_comment, "hasNotReadNotes": False,
         "media": media, "mediaAltText": [], "providers": [{"network": prov}],
         "publicationDate": {"dateTime": dt, "timezone": "Asia/Seoul"}, "shortener": False,
         "smartLinkData": {"ids": []}, "text": text}
    x.update(extra)
    return x


for p in d["posts"]:
    text = p["caption"] + "\n\n" + " ".join(p["hashtags"])
    cards = [B + f for f in sorted(glob.glob(f"out/{p['id']}/card_*.png"))]
    vid = B + f"out/{p['id']}/shorts.mp4"
    # 인스타 카드뉴스(캐러셀)는 수·일만 (사용자 요청: 카드뉴스 1/3로, 릴스 위주). 나머지 날은 릴스 1개.
    wd = datetime.date.fromisoformat(p["date"]).weekday()  # 월0 … 일6
    carousel = p.get("carousel", wd in (2, 6)) and not p.get("shorts_only")
    reel_hm = "12:30" if p.get("reels") else "21:00"
    if carousel:
        rows = [("IG", "21:00", base(p["date"] + "T21:00:00", text, cards, "instagram",
                                 {"instagramData": {"type": "POST", "isAiGenerated": True}}, p.get("first_comment", "")))]
        reel_hm = "21:00"
    else:
        rows = [("REEL", reel_hm, base(p["date"] + f"T{reel_hm}:00", text, [vid], "instagram",
                                       {"instagramData": {"type": "REEL", "showReelOnFeed": True, "isAiGenerated": True}},
                                       p.get("first_comment", "")))]
    yt = p["shorts_title"] + "\n\n" + p["caption"] + "\n\n" + " ".join(p["hashtags"][:5]) + " #shorts"
    # 유튜브 쇼츠는 릴스와 같은 시간
    yt_hm = reel_hm
    rows.append(("YT", yt_hm, base(p["date"] + f"T{yt_hm}:00", yt, [vid], "youtube",
                                     {"youtubeData": {"title": p["shorts_title"][:100], "type": "short", "privacy": "public",
                                                      "tags": [h.strip("#") for h in p["hashtags"]], "category": "PEOPLE_BLOGS",
                                                      "madeForKids": False, "isAiGeneratedContent": False}})))
    if p.get("threads"):
        th_media = [vid] if p.get("shorts_only") else cards[:1]
        rows.append(("TH", "21:00", base(p["date"] + "T21:00:00", p["threads"], th_media, "threads", {"threadsData": {}})))
    for kind, hm, info in rows:
        print(f"=== {p['id']} {kind} {p['date']}T{hm}:00+09:00")
        print(json.dumps(info, ensure_ascii=False))
