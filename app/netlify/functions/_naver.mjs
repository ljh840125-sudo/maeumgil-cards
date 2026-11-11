// 네이버 API 도우미: 검색광고(키워드 도구) · 검색(블로그) · 데이터랩 · 블로그 본문 읽기
import crypto from "node:crypto";

export const env = () => ({
  adKey: process.env.NAVER_AD_API_KEY, adSecret: process.env.NAVER_AD_SECRET, adCustomer: process.env.NAVER_AD_CUSTOMER_ID,
  cid: process.env.NAVER_CLIENT_ID, csecret: process.env.NAVER_CLIENT_SECRET,
});
export const hasAd = () => { const e = env(); return !!(e.adKey && e.adSecret && e.adCustomer); };
export const hasSearch = () => { const e = env(); return !!(e.cid && e.csecret); };

const num = (v) => (typeof v === "number" ? v : /</.test(String(v)) ? 5 : Number(String(v).replace(/[^\d.]/g, "")) || 0);

// 검색광고 키워드 도구: 연관 키워드 + 월 검색량(PC/모바일)
export async function keywordTool(hints) {
  const e = env();
  const ts = String(Date.now());
  const path = "/keywordstool";
  const sig = crypto.createHmac("sha256", e.adSecret).update(`${ts}.GET.${path}`).digest("base64");
  const q = hints.map((h) => h.replace(/\s+/g, "")).filter(Boolean).slice(0, 5).join(",");
  const r = await fetch(`https://api.searchad.naver.com${path}?hintKeywords=${encodeURIComponent(q)}&showDetail=1`, {
    headers: { "X-Timestamp": ts, "X-API-KEY": e.adKey, "X-Customer": String(e.adCustomer), "X-Signature": sig },
  });
  const j = await r.json().catch(() => ({}));
  if (!r.ok) throw new Error("검색광고 API: " + (j?.title || j?.message || r.status));
  return (j.keywordList || []).map((k) => {
    const pc = num(k.monthlyPcQcCnt), mo = num(k.monthlyMobileQcCnt);
    return { kw: k.relKeyword, pc, mo, vol: pc + mo, comp: k.compIdx || "", clk: num(k.monthlyAvePcClkCnt) + num(k.monthlyAveMobileClkCnt) };
  });
}

// 블로그 검색: 문서 수(발행량) + 상위 글
export async function blogSearch(query, display = 10) {
  const e = env();
  const r = await fetch(`https://openapi.naver.com/v1/search/blog.json?query=${encodeURIComponent(query)}&display=${display}&sort=sim`, {
    headers: { "X-Naver-Client-Id": e.cid, "X-Naver-Client-Secret": e.csecret },
  });
  const j = await r.json().catch(() => ({}));
  if (!r.ok) throw new Error("검색 API: " + (j?.errorMessage || r.status));
  const clean = (s) => String(s || "").replace(/<[^>]+>/g, "").replace(/&quot;/g, '"').replace(/&amp;/g, "&").replace(/&lt;/g, "<").replace(/&gt;/g, ">").replace(/&#39;/g, "'");
  return {
    total: j.total || 0,
    items: (j.items || []).map((it) => ({ title: clean(it.title), link: it.link, desc: clean(it.description), blogger: clean(it.bloggername), date: it.postdate })),
  };
}

// 데이터랩: 최근 12개월 월별 검색 추이(상대값)
export async function trend(keyword) {
  const e = env();
  const end = new Date(), start = new Date(); start.setMonth(start.getMonth() - 12);
  const d = (x) => x.toISOString().slice(0, 10);
  const r = await fetch("https://openapi.naver.com/v1/datalab/search", {
    method: "POST",
    headers: { "X-Naver-Client-Id": e.cid, "X-Naver-Client-Secret": e.csecret, "content-type": "application/json" },
    body: JSON.stringify({ startDate: d(start), endDate: d(end), timeUnit: "month", keywordGroups: [{ groupName: keyword, keywords: [keyword] }] }),
  });
  const j = await r.json().catch(() => ({}));
  if (!r.ok) return null;
  return (j.results?.[0]?.data || []).map((p) => ({ m: p.period.slice(0, 7), v: Math.round(p.ratio) }));
}

// 네이버 블로그 글 본문 읽기 (모바일 페이지)
export function parsePost(html) {
  let area = "";
  const i = html.indexOf("se-main-container");
  if (i >= 0) {
    area = html.slice(Math.max(0, html.lastIndexOf("<", i)));
    const cut = area.search(/class="[^"]*(post_footer|section_t1|comment_area|wrap_postcomment)/);
    if (cut > 0) area = area.slice(0, area.lastIndexOf("<", cut));
  } else {
    const k = html.indexOf('id="postViewArea"');
    if (k >= 0) area = html.slice(html.lastIndexOf("<", k), k + 200000);
  }
  if (!area) return null;
  const images = (area.match(/class="[^"]*se-image-resource/g) || []).length || (area.match(/<img /g) || []).length;
  const quotes = (area.match(/class="[^"]*se-component se-quotation/g) || []).length;
  const titles = (area.match(/class="[^"]*se-component se-sectionTitle/g) || []).length;
  const videos = (area.match(/class="[^"]*se-component se-video/g) || []).length;
  const maps = (area.match(/class="[^"]*se-component se-placesMap/g) || []).length;
  const text = area
    .replace(/<script[\s\S]*?<\/script>/g, " ").replace(/<style[\s\S]*?<\/style>/g, " ")
    .replace(/<\/(p|div|li|h\d)>/g, "\n").replace(/<br\s*\/?>/g, "\n").replace(/<[^>]+>/g, " ")
    .replace(/&nbsp;/g, " ").replace(/&quot;/g, '"').replace(/&amp;/g, "&").replace(/&lt;/g, "<").replace(/&gt;/g, ">").replace(/&#39;/g, "'").replace(/&#x200B;|​/g, "")
    .split("\n").map((l) => l.replace(/\s+/g, " ").trim()).filter(Boolean).join("\n");
  return { text, chars: text.replace(/\s/g, "").length, images, subheads: quotes + titles, videos, maps };
}
export async function readPost(link) {
  const m = String(link).match(/blog\.naver\.com\/(?:PostView\.n(?:aver|hn)\?blogId=)?([\w-]+)(?:\/|&logNo=)(\d+)/);
  if (!m) return null;
  const url = `https://m.blog.naver.com/${m[1]}/${m[2]}`;
  const r = await fetch(url, { headers: { "user-agent": "Mozilla/5.0 (Linux; Android 14) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126 Mobile Safari/537.36", "accept-language": "ko-KR,ko" } });
  if (!r.ok) return null;
  return parsePost(await r.text());
}

// 동시에 n개씩
export async function pool(items, n, fn) {
  const out = new Array(items.length); let i = 0;
  await Promise.all(Array.from({ length: Math.min(n, items.length) }, async () => {
    while (i < items.length) { const k = i++; try { out[k] = await fn(items[k], k); } catch { out[k] = null; } }
  }));
  return out;
}
