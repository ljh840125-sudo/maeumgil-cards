import { json, authorized } from "./_lib.mjs";
// 무료 사진 검색 (Pexels: 상업적 사용 무료)
export const handler = async (event) => {
  const a = authorized(event); if (!a.ok) return a.res;
  const key = process.env.PEXELS_API_KEY;
  if (!key) return json(400, { error: "넷리파이 환경변수 PEXELS_API_KEY가 없어요." });
  const q = (event.queryStringParameters?.q || "").slice(0, 100).trim();
  if (!q) return json(400, { error: "검색어가 없어요." });
  const orient = event.queryStringParameters?.o === "square" ? "square" : "landscape";
  const r = await fetch(`https://api.pexels.com/v1/search?query=${encodeURIComponent(q)}&per_page=8&orientation=${orient}`, {
    headers: { Authorization: key },
  });
  const j = await r.json().catch(() => ({}));
  if (!r.ok) return json(502, { error: "Pexels: " + (j?.error || r.status) });
  const photos = (j.photos || []).map((p) => ({
    src: p.src?.large || p.src?.medium, thumb: p.src?.tiny, alt: p.alt || "", photographer: p.photographer || "", page: p.url,
  })).filter((p) => p.src);
  return json(200, { photos });
};
