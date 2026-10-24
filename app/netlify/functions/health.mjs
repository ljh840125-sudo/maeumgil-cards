import { json, authorized } from "./_lib.mjs";
// 어떤 기능이 켜져 있는지 알려줌 (키 값은 절대 보내지 않음)
export const handler = async (event) => {
  const info = {
    app: "blog-gongbang",
    password: !!process.env.APP_PASSWORD,
    anthropic: !!process.env.ANTHROPIC_API_KEY,
    openai: !!process.env.OPENAI_API_KEY,
    pexels: !!process.env.PEXELS_API_KEY,
  };
  if (event.queryStringParameters?.auth) {
    const a = authorized(event);
    info.authOk = a.ok;
  }
  return json(200, info);
};
