import { connectLambda, getStore } from "@netlify/blobs";
import { json, authorized } from "./_lib.mjs";
// 오래 걸리는 작업(글쓰기·AI 그림)의 진행 상황 확인
export const handler = async (event) => {
  const a = authorized(event); if (!a.ok) return a.res;
  connectLambda(event);
  const id = event.queryStringParameters?.id || "";
  if (!/^[\w-]{8,80}$/.test(id)) return json(400, { error: "bad id" });
  const store = getStore("jobs");
  const v = await store.get(id, { type: "json" });
  if (!v) return json(200, { status: "pending" });
  if (v.status !== "pending") await store.delete(id);
  return json(200, v);
};
