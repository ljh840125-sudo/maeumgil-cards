import { json, authorized } from "./_lib.mjs";
// Pexels 사진을 대신 받아서 넘겨줌 (본문에 사진째 복사하려면 필요)
export const handler = async (event) => {
  const a = authorized(event); if (!a.ok) return a.res;
  const u = event.queryStringParameters?.u || "";
  if (!/^https:\/\/images\.pexels\.com\//.test(u)) return json(400, { error: "허용되지 않은 주소" });
  const r = await fetch(u);
  if (!r.ok) return json(502, { error: "사진을 받지 못했어요." });
  const buf = Buffer.from(await r.arrayBuffer());
  return {
    statusCode: 200,
    headers: { "content-type": r.headers.get("content-type") || "image/jpeg", "cache-control": "public, max-age=86400" },
    body: buf.toString("base64"),
    isBase64Encoded: true,
  };
};
