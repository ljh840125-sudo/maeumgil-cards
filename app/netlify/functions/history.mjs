import { connectLambda, getStore } from "@netlify/blobs";
import { json, authorized } from "./_lib.mjs";
// 내 원고 목록 (넷리파이 서버 저장 · 앱 비밀번호로 보호)
// GET: 목록 / POST {id, ...}: 저장·수정 / DELETE ?id=: 삭제
const KEY = "posts";
export const handler = async (event) => {
  const a = authorized(event); if (!a.ok) return a.res;
  connectLambda(event);
  const store = getStore("history");
  const list = (await store.get(KEY, { type: "json" })) || [];
  if (event.httpMethod === "GET") return json(200, { items: list });
  if (event.httpMethod === "POST") {
    let e; try { e = JSON.parse(event.body || "{}"); } catch { return json(400, { error: "형식이 맞지 않아요." }); }
    if (!/^[\w-]{4,40}$/.test(e.id || "")) return json(400, { error: "id가 없어요." });
    const body = JSON.stringify(e);
    if (body.length > 200000) return json(400, { error: "원고가 너무 커요." });
    const k = list.findIndex((x) => x.id === e.id);
    if (k >= 0) list[k] = e; else list.unshift(e);
    list.sort((x, y) => (y.at || 0) - (x.at || 0));
    await store.setJSON(KEY, list.slice(0, 500));
    return json(200, { ok: true });
  }
  if (event.httpMethod === "DELETE") {
    const id = event.queryStringParameters?.id || "";
    await store.setJSON(KEY, list.filter((x) => x.id !== id));
    return json(200, { ok: true });
  }
  return json(405, { error: "지원하지 않는 요청" });
};
