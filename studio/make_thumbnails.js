// Thumbnails / covers for story episodes (YouTube Shorts, Instagram Reels, TikTok).
//
//   node studio/make_thumbnails.js 2 3 4 5        -> branding/thumbnails/story_00N_partK_ur.jpg
//
// 1080x1920 (the 9:16 cover all three apps take). Everything important sits inside the
// centre 1080x1440 band (y 240-1680), so Instagram's 3:4 profile-grid crop keeps it.
// Part 1: title, the three suspects with their numbers, Foxley with his magnifier, "1, 2 YA 3?".
// Part 2: same line-up (no spoiler: the culprit is not shown on the cover), "JAWAB!" and
// "KAUN THA MUJRIM?". Art comes from sets/ and puppet/cast/ (the cleaned cut-outs).
// Font: Nunito, the same face the videos use, from the HyperFrames font cache (subset files,
// combined here with unicode-range).
const fs = require("fs");
const path = require("path");
const { chromium } = require("playwright");
const fontkit = require("fontkit");

const ROOT = path.resolve(__dirname, "..");
const OUT = path.join(ROOT, "branding", "thumbnails");
const FONT_DIR = "/root/.cache/hyperframes/fonts/nunito";
const W = 1080, H = 1920;

function fontCss() {
  if (!fs.existsSync(FONT_DIR)) return "";
  let css = "";
  for (const f of fs.readdirSync(FONT_DIR).filter((x) => /^(800|900)-normal/.test(x))) {
    const cps = fontkit.openSync(path.join(FONT_DIR, f)).characterSet;
    const range = cps.map((c) => "U+" + c.toString(16).toUpperCase()).join(",");
    const data = fs.readFileSync(path.join(FONT_DIR, f)).toString("base64");
    css += `@font-face{font-family:"Nunito";font-weight:${f.slice(0, 3)};src:url(data:font/woff2;base64,${data}) format("woff2");unicode-range:${range};}\n`;
  }
  return css;
}

const img = (p) => "data:image/png;base64," + fs.readFileSync(path.join(ROOT, p)).toString("base64");
const rig = (id) => JSON.parse(fs.readFileSync(path.join(ROOT, "puppet", "cast", id, "rig.json")));
const esc = (s) => String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;");

function figure(id, pose, cx, feetY, baseH, flip) {
  const r = rig(id);
  const p = r.poses.includes(pose) ? pose : r.talk_pose;
  const s = (baseH * r.height) / r.figure_height;
  const w = r.canvas[0] * s, h = r.canvas[1] * s;
  const tr = flip && r.facing !== "front" ? "transform:scaleX(-1);" : "";
  return { html: `<img src="${img(`puppet/cast/${id}/pose_${p}.png`)}" style="position:absolute;left:${cx - w / 2}px;top:${feetY - h}px;width:${w}px;height:${h}px;${tr}">`,
           top: feetY - baseH * r.height, cx };
}

function page(ep, part, fonts) {
  const p1 = JSON.parse(fs.readFileSync(path.join(ROOT, "episodes", `s${String(ep).padStart(3, "0")}_part1.json`)));
  const lu = p1.shots.find((s) => s.lineup);
  const title = p1.title.ur, titleEn = p1.title.en;
  const bg = img(`sets/${lu.set}/background.png`);
  // suspects
  const xs = [0.2, 0.5, 0.8].map((f) => f * W);
  let people = "", nums = "";
  lu.lineup.forEach((id, k) => {
    const f = figure(id, "nervous", xs[k], 1400, 520, false);
    people += f.html;
    nums += `<div class="num" style="left:${f.cx - 62}px;top:${f.top - 132}px">${k + 1}</div>`;
  });
  const fox = figure("foxley", part === 1 ? "examine" : "point", 200, 1900, 540, part === 2);
  const big = part === 1
    ? `<div class="big"><div class="q">1, 2 YA 3?</div><div class="ask">KAUN JHOOTA HAI?</div></div>`
    : `<div class="big two"><div class="q jawab">JAWAB!</div><div class="ask">KAUN THA MUJRIM?</div></div>`;
  const tag = part === 1 ? "PART 1" : "PART 2 · JAWAB";
  return `<!doctype html><html><head><meta charset="utf-8"><style>
${fonts}
*{margin:0;padding:0;box-sizing:border-box}
html,body{width:${W}px;height:${H}px;overflow:hidden;background:#111}
#c{position:relative;width:${W}px;height:${H}px;overflow:hidden;font-family:"Nunito",sans-serif}
.bg{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;filter:saturate(1.1) brightness(0.92)}
.shade{position:absolute;inset:0;background:linear-gradient(180deg,rgba(8,10,30,.72) 0%,rgba(8,10,30,.15) 30%,rgba(8,10,30,0) 55%,rgba(8,10,30,.55) 78%,rgba(8,10,30,.85) 100%)}
.spot{position:absolute;inset:0;background:radial-gradient(ellipse 70% 30% at 50% 58%,rgba(255,230,160,.22),rgba(0,0,0,0) 70%)}
.case{position:absolute;left:40px;top:262px}
.case span{display:inline-block;background:#F2B134;color:#2B2B2B;font-weight:900;font-size:40px;letter-spacing:.1em;padding:8px 26px;border-radius:40px;border:6px solid #2B2B2B}
.part{position:absolute;right:40px;top:258px;background:#1F4E5F;color:#fff;font-weight:900;font-size:34px;padding:10px 22px;border-radius:20px;border:6px solid #2B2B2B;transform:rotate(4deg)}
.title{position:absolute;left:40px;right:40px;top:350px;text-align:center}
.title .t{display:inline-block;background:#C8342B;color:#fff;font-weight:900;font-size:112px;line-height:1.0;padding:24px 36px 28px;border-radius:34px;border:10px solid #2B2B2B;box-shadow:0 16px 0 #2B2B2B;transform:rotate(-2deg)}
.title .en{margin-top:26px;color:#fff;font-weight:800;font-size:40px;letter-spacing:.06em;text-shadow:0 3px 0 #000,0 0 14px rgba(0,0,0,.8)}
.num{position:absolute;width:124px;height:124px;border-radius:50%;background:#F2B134;border:9px solid #2B2B2B;display:flex;align-items:center;justify-content:center;font-weight:900;font-size:76px;color:#2B2B2B;box-shadow:0 8px 0 #2B2B2B}
.big{position:absolute;right:16px;top:1428px;width:700px;text-align:center}
.big .q{font-weight:900;font-size:122px;line-height:1;white-space:nowrap;color:#FFD23F;transform:rotate(-3deg);
  text-shadow:-8px -8px 0 #2B2B2B,8px -8px 0 #2B2B2B,-8px 8px 0 #2B2B2B,8px 8px 0 #2B2B2B,0 14px 0 #2B2B2B,0 18px 20px rgba(0,0,0,.6)}
.big .q.jawab{color:#fff;background:#2E9E4F;border:10px solid #2B2B2B;border-radius:32px;padding:14px 10px 22px;box-shadow:0 14px 0 #2B2B2B;text-shadow:none}
.big .ask{display:inline-block;margin-top:18px;background:#fff;color:#2B2B2B;font-weight:900;font-size:50px;padding:10px 26px;border-radius:24px;border:7px solid #2B2B2B;transform:rotate(-2deg)}
</style></head><body><div id="c">
<img class="bg" src="${bg}"><div class="spot"></div>${people}<div class="shade"></div>${nums}${fox.html}
<div class="case"><span>FOXLEY CASE #${ep}</span></div><div class="part">${tag}</div>
<div class="title"><div class="t">${esc(title)}</div><div class="en">${esc(titleEn)}</div></div>
${big}
</div></body></html>`;
}

(async () => {
  const eps = process.argv.slice(2).map(Number);
  if (!eps.length) { console.error("usage: node studio/make_thumbnails.js 2 3 4 5"); process.exit(1); }
  fs.mkdirSync(OUT, { recursive: true });
  const fonts = fontCss();
  const browser = await chromium.launch();
  const pg = await browser.newPage({ viewport: { width: W, height: H }, deviceScaleFactor: 1 });
  for (const ep of eps) for (const part of [1, 2]) {
    await pg.setContent(page(ep, part, fonts), { waitUntil: "load" });
    await pg.evaluate(() => document.fonts.ready);
    const out = path.join(OUT, `story_${String(ep).padStart(3, "0")}_part${part}_ur.jpg`);
    await pg.screenshot({ path: out, type: "jpeg", quality: 92 });
    console.log(out);
  }
  await browser.close();
})();
