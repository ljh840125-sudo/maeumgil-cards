import { connectLambda, getStore } from "@netlify/blobs";
import { json, authorized } from "./_lib.mjs";
// 사진 1장(JPG)을 임시 저장하고 열쇠(key)를 돌려줌
export const handler = async (event) => {
  const a = authorized(event); if (!a.ok) return a.res;
  if (event.httpMethod !== "POST") return json(405, { error: "POST only" });
  connectLambda(event);
  const buf = Buffer.from(event.body || "", event.isBase64Encoded ? "base64" : "binary");
  if (!buf.length || buf.length > 5_500_000) return json(400, { error: "사진 크기가 맞지 않아요." });
  const key = `u-${Date.now()}-${Math.random().toString(36).slice(2, 10)}`;
  await getStore("uploads").set(key, buf);
  return json(200, { key });
};
