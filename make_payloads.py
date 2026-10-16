"""주간 JSON → Metricool 예약 payload 목록 출력.

사용법: python3 make_payloads.py content/<주시작일>.json <커밋SHA>
각 줄: === <post id> <IG|REEL|YT> <ISO 날짜시간+09:00>  다음 줄에 info JSON
"""
import glob
import json
import sys

src, sha = sys.argv[1], sys.argv[2]
B = f"https://raw.githubusercontent.com/ljh840125-sudo/maeumgil-cards/{sha}/"
d = json.load(open(src, encoding="utf-8"))


def base(dt, text, media, prov, extra):
    x = {"autoPublish": True, "draft": False, "descendants": [], "firstCommentText": "", "hasNotReadNotes": False,
         "media": media, "mediaAltText": [], "providers": [{"network": prov}],
         "publicationDate": {"dateTime": dt, "timezone": "Asia/Seoul"}, "shortener": False,
         "smartLinkData": {"ids": []}, "text": text}
    x.update(extra)
    return x


for p in d["posts"]:
    text = p["caption"] + "\n\n" + " ".join(p["hashtags"])
    cards = [B + f for f in sorted(glob.glob(f"out/{p['id']}/card_*.png"))]
    vid = B + f"out/{p['id']}/shorts.mp4"
    if p.get("shorts_only"):
        rows = [("REEL", "21:00", base(p["date"] + "T21:00:00", text, [vid], "instagram",
                                       {"instagramData": {"type": "REEL", "showReelOnFeed": True, "isAiGenerated": True}}))]
    else:
        rows = [("IG", "21:00", base(p["date"] + "T21:00:00", text, cards, "instagram",
                                 {"instagramData": {"type": "POST", "isAiGenerated": True}}))]
    if p.get("reels") and not p.get("shorts_only"):
        rows.append(("REEL", "12:30", base(p["date"] + "T12:30:00", text, [vid], "instagram",
                                           {"instagramData": {"type": "REEL", "showReelOnFeed": False, "isAiGenerated": True}})))
    yt = p["shorts_title"] + "\n\n" + p["caption"] + "\n\n" + " ".join(p["hashtags"][:5]) + " #shorts"
    rows.append(("YT", "21:00", base(p["date"] + "T21:00:00", yt, [vid], "youtube",
                                     {"youtubeData": {"title": p["shorts_title"][:100], "type": "short", "privacy": "public",
                                                      "tags": [h.strip("#") for h in p["hashtags"]], "category": "PEOPLE_BLOGS",
                                                      "madeForKids": False, "isAiGeneratedContent": False}})))
    for kind, hm, info in rows:
        print(f"=== {p['id']} {kind} {p['date']}T{hm}:00+09:00")
        print(json.dumps(info, ensure_ascii=False))
