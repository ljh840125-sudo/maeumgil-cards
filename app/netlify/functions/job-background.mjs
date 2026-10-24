import { connectLambda, getStore } from "@netlify/blobs";
import { authorized } from "./_lib.mjs";
// 백그라운드 작업 (최대 15분): 글쓰기(Claude API) 또는 AI 그림(OpenAI)
// 이름 끝의 -background 때문에 넷리파이가 바로 202를 돌려주고 뒤에서 실행함
export const handler = async (event) => {
  const a = authorized(event); if (!a.ok) return a.res;
  connectLambda(event);
  let req;
  try { req = JSON.parse(event.body || "{}"); } catch { return; }
  const { id, kind } = req;
  if (!/^[\w-]{8,80}$/.test(id || "")) return;
  const jobs = getStore("jobs");
  await jobs.setJSON(id, { status: "pending" });
  try {
    let result;
    if (kind === "write") result = await write(req);
    else if (kind === "image") result = await image(req);
    else throw new Error("unknown job");
    await jobs.setJSON(id, { status: "done", result });
  } catch (e) {
    await jobs.setJSON(id, { status: "error", error: String(e?.message || e).slice(0, 400) });
  }
};

async function write({ prompt, imageKeys = [] }) {
  const key = process.env.ANTHROPIC_API_KEY;
  if (!key) throw new Error("넷리파이 환경변수 ANTHROPIC_API_KEY가 없어요.");
  const uploads = getStore("uploads");
  const content = [];
  for (const k of imageKeys.slice(0, 20)) {
    const buf = await uploads.get(k, { type: "arrayBuffer" });
    if (!buf) continue;
    content.push({ type: "image", source: { type: "base64", media_type: "image/jpeg", data: Buffer.from(buf).toString("base64") } });
    await uploads.delete(k);
  }
  content.push({ type: "text", text: String(prompt || "").slice(0, 200000) });
  const r = await fetch("https://api.anthropic.com/v1/messages", {
    method: "POST",
    headers: { "x-api-key": key, "anthropic-version": "2023-06-01", "content-type": "application/json" },
    body: JSON.stringify({
      model: process.env.ANTHROPIC_MODEL || "claude-sonnet-5-5",
      max_tokens: 8000,
      messages: [{ role: "user", content }],
    }),
  });
  const j = await r.json().catch(() => ({}));
  if (!r.ok) throw new Error("Claude API: " + (j?.error?.message || r.status));
  return (j.content || []).filter((b) => b.type === "text").map((b) => b.text).join("");
}

async function image({ prompt, size }) {
  const key = process.env.OPENAI_API_KEY;
  if (!key) throw new Error("넷리파이 환경변수 OPENAI_API_KEY가 없어요.");
  const r = await fetch("https://api.openai.com/v1/images/generations", {
    method: "POST",
    headers: { Authorization: `Bearer ${key}`, "content-type": "application/json" },
    body: JSON.stringify({
      model: process.env.OPENAI_IMAGE_MODEL || "gpt-image-1",
      prompt: String(prompt || "").slice(0, 3000),
      size: ["1024x1024", "1536x1024", "1024x1536"].includes(size) ? size : "1024x1024",
      quality: process.env.OPENAI_IMAGE_QUALITY || "medium",
      n: 1,
    }),
  });
  const j = await r.json().catch(() => ({}));
  if (!r.ok) throw new Error("OpenAI: " + (j?.error?.message || r.status));
  const b64 = j?.data?.[0]?.b64_json;
  if (!b64) throw new Error("OpenAI가 이미지를 돌려주지 않았어요.");
  return { b64 };
}
