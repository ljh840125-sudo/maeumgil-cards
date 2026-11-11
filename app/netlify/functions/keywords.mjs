import { json, authorized } from "./_lib.mjs";
import { keywordTool, blogSearch, hasAd, hasSearch, pool } from "./_naver.mjs";
// 씨앗 키워드 → 연관 키워드 + 월 검색량 + 블로그 문서 수 + 경쟁 비율 + 등급
export const handler = async (event) => {
  const a = authorized(event); if (!a.ok) return a.res;
  if (!hasAd()) return json(400, { error: "넷리파이 환경변수에 네이버 검색광고 API 키 3개(NAVER_AD_API_KEY, NAVER_AD_SECRET, NAVER_AD_CUSTOMER_ID)를 넣어 주세요." });
  const raw = (event.queryStringParameters?.q || "").slice(0, 120);
  const seeds = raw.split(",").map((s) => s.trim()).filter(Boolean).slice(0, 5);
  if (!seeds.length) return json(400, { error: "키워드를 넣어 주세요." });
  const min = Number(event.queryStringParameters?.min || 0), max = Number(event.queryStringParameters?.max || 1e9);
  try {
    let list = await keywordTool(seeds);
    const seedSet = new Set(seeds.map((s) => s.replace(/\s+/g, "")));
    // 씨앗 키워드는 항상 포함, 나머지는 범위 안에서 검색량 순
    const inRange = list.filter((k) => seedSet.has(k.kw) || (k.vol >= min && k.vol <= max));
    inRange.sort((x, y) => (seedSet.has(y.kw) - seedSet.has(x.kw)) || y.vol - x.vol);
    const pick = inRange.slice(0, 30);
    if (hasSearch()) {
      const totals = await pool(pick, 6, async (k) => (await blogSearch(k.kw, 1)).total);
      pick.forEach((k, i) => { k.docs = totals[i]; });
    }
    for (const k of pick) {
      if (k.docs == null) { k.ratio = null; k.grade = "?"; k.score = 0; continue; }
      k.ratio = k.vol ? +(k.docs / k.vol).toFixed(2) : null;
      k.grade = k.vol < 50 ? "검색 적음" : k.ratio < 0.5 ? "황금" : k.ratio < 1.5 ? "좋음" : k.ratio < 5 ? "보통" : "어려움";
      // 황금지수: 검색량은 많을수록, 문서 수는 적을수록
      k.score = k.vol < 50 ? 0 : Math.round((Math.log10(k.vol + 1) * 30) / Math.max(0.2, Math.sqrt(k.ratio || 0.01)));
    }
    pick.sort((x, y) => (seedSet.has(y.kw) - seedSet.has(x.kw)) || y.score - x.score || y.vol - x.vol);
    return json(200, { seeds, total: list.length, keywords: pick, docsAvailable: hasSearch() });
  } catch (e) {
    return json(502, { error: String(e.message || e) });
  }
};
