import { json, authorized } from "./_lib.mjs";
import { blogSearch, readPost, trend, hasSearch, pool } from "./_naver.mjs";
// 키워드 → 네이버 블로그 상위 3개 글 분석 + 12개월 검색 추이
export const handler = async (event) => {
  const a = authorized(event); if (!a.ok) return a.res;
  if (!hasSearch()) return json(400, { error: "넷리파이 환경변수에 네이버 개발자센터 키(NAVER_CLIENT_ID, NAVER_CLIENT_SECRET)를 넣어 주세요." });
  const q = (event.queryStringParameters?.q || "").trim().slice(0, 60);
  if (!q) return json(400, { error: "키워드를 넣어 주세요." });
  try {
    const [res, tr] = await Promise.all([blogSearch(q, 10), trend(q).catch(() => null)]);
    const naver = res.items.filter((it) => /blog\.naver\.com/.test(it.link)).slice(0, 3);
    const posts = await pool(naver, 3, async (it) => {
      const p = await readPost(it.link);
      return { ...it, ...(p ? { chars: p.chars, images: p.images, subheads: p.subheads, videos: p.videos, maps: p.maps, excerpt: p.text.slice(0, 1500) } : { unread: true }) };
    });
    const read = posts.filter((p) => p && !p.unread);
    const avg = (f) => (read.length ? Math.round(read.reduce((s, p) => s + (p[f] || 0), 0) / read.length) : null);
    let season = null;
    if (tr && tr.length >= 6) {
      const all = tr.reduce((s, p) => s + p.v, 0) / tr.length;
      const last3 = tr.slice(-3).reduce((s, p) => s + p.v, 0) / 3;
      season = { last3: Math.round(last3), avg: Math.round(all), dir: last3 > all * 1.2 ? "상승" : last3 < all * 0.8 ? "하락" : "꾸준" };
    }
    return json(200, {
      keyword: q, docs: res.total, posts: posts.filter(Boolean), trend: tr, season,
      avg: { chars: avg("chars"), images: avg("images"), subheads: avg("subheads") },
      others: res.items.slice(0, 10).map((it) => ({ title: it.title, link: it.link, date: it.date })),
    });
  } catch (e) {
    return json(502, { error: String(e.message || e) });
  }
};
