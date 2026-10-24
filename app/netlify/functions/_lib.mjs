// 공통: 비밀번호 확인, 응답 도우미
export const json = (status, body) => ({
  statusCode: status,
  headers: { "content-type": "application/json; charset=utf-8", "cache-control": "no-store" },
  body: JSON.stringify(body),
});

export function authorized(event) {
  const pw = process.env.APP_PASSWORD;
  if (!pw) return { ok: false, res: json(500, { error: "넷리파이 환경변수 APP_PASSWORD를 먼저 설정해 주세요." }) };
  const h = event.headers || {};
  const got = h["x-app-key"] || h["X-App-Key"];
  if (got !== pw) return { ok: false, res: json(401, { error: "앱 비밀번호가 맞지 않아요." }) };
  return { ok: true };
}
