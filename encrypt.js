#!/usr/bin/env node
/*
 * encrypt.js — turns src/index.template.html into an encrypted public/index.html.
 * The whole app (with the latest jobs inlined) is AES-256-GCM encrypted; the key
 * is derived from the PIN via PBKDF2-SHA256. Only ciphertext + a small unlock
 * page ship publicly. PIN: env SITE_PIN, default "2452".
 *
 * NOTE: a 4-digit PIN is only 10,000 combinations — stops casual access, not a
 * determined attacker. Use a longer SITE_PIN for real protection.
 */
const fs = require("fs");
const path = require("path");
const crypto = require("crypto");

const PIN = process.env.SITE_PIN || "2452";
const ITER = 200000;
const ROOT = __dirname;
const TEMPLATE = path.join(ROOT, "src", "index.template.html");
const JOBS = path.join(ROOT, "fetcher", "jobs.json");
const OUT = path.join(ROOT, "public", "index.html");

let html = fs.readFileSync(TEMPLATE, "utf8");

if (fs.existsSync(JOBS)) {
  const data = JSON.parse(fs.readFileSync(JOBS, "utf8"));
  const inject =
    `<script>window.__JOBS=${JSON.stringify(data.jobs || [])};` +
    `window.__META=${JSON.stringify({ updated: data.updated || "" })};</script>`;
  html = html.replace("</head>", inject + "\n</head>");
  console.log(`inlined ${(data.jobs || []).length} jobs (updated ${data.updated || "?"})`);
} else {
  console.log("no fetcher/jobs.json found — app will use its built-in sample data");
}

const salt = crypto.randomBytes(16);
const iv = crypto.randomBytes(12);
const key = crypto.pbkdf2Sync(PIN, salt, ITER, 32, "sha256");
const cipher = crypto.createCipheriv("aes-256-gcm", key, iv);
const ct = Buffer.concat([cipher.update(html, "utf8"), cipher.final()]);
const tag = cipher.getAuthTag();
const payload = {
  v: 1, iterations: ITER,
  salt: salt.toString("base64"),
  iv: iv.toString("base64"),
  ct: Buffer.concat([ct, tag]).toString("base64"),
};

fs.writeFileSync(OUT, shell(JSON.stringify(payload)), "utf8");
console.log(`wrote ${path.relative(ROOT, OUT)} (encrypted, ${Math.round(payload.ct.length / 1024)} KB)`);

/* --------------------------------------------------------------------------- */
function shell(payloadJson) {
  return `<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
<meta name="robots" content="noindex, nofollow"/>
<title>The Job Hunt</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Bungee&family=Plus+Jakarta+Sans:wght@500;700;800&family=JetBrains+Mono:wght@700&display=swap" rel="stylesheet">
<style>
  *{box-sizing:border-box;margin:0;padding:0}
  :root{--cyan:#06b6d4;--blue:#2563eb;--violet:#8b5cf6;--pink:#ec4899;--amber:#f59e0b;--ink:#0f1b33}
  body{min-height:100vh;display:grid;place-items:center;padding:24px;
    font-family:'Plus Jakarta Sans',system-ui,sans-serif;color:var(--ink);background:#f4f8fd;
    background-image:radial-gradient(circle at 15% 20%,rgba(6,182,212,.10),transparent 8%),
      radial-gradient(circle at 85% 15%,rgba(236,72,153,.10),transparent 8%),
      radial-gradient(circle at 78% 82%,rgba(37,99,235,.10),transparent 9%),
      radial-gradient(circle at 22% 85%,rgba(245,158,11,.12),transparent 8%),
      radial-gradient(circle at 50% 50%,rgba(139,92,246,.05),transparent 40%);
    overflow:hidden}
  /* floating funky stickers */
  .sticker{position:fixed;font-family:'Bungee';font-size:clamp(28px,6vw,64px);opacity:.14;user-select:none;pointer-events:none;z-index:0}
  .s1{top:8%;left:6%;color:var(--cyan);transform:rotate(-14deg)}
  .s2{bottom:10%;right:7%;color:var(--pink);transform:rotate(12deg)}
  .s3{top:14%;right:10%;color:var(--amber);transform:rotate(8deg);font-size:clamp(20px,4vw,40px)}
  .s4{bottom:14%;left:9%;color:var(--violet);transform:rotate(-9deg);font-size:clamp(20px,4vw,40px)}

  .card{position:relative;z-index:2;width:min(430px,92vw);text-align:center;padding:40px 34px 30px;
    background:#fff;border-radius:20px;
    box-shadow:14px 14px 0 rgba(6,182,212,.14), -10px 18px 40px rgba(37,99,235,.14), 0 2px 6px rgba(15,27,51,.06)}
  .logo{width:66px;height:66px;margin:0 auto 20px;border-radius:18px;display:grid;place-items:center;
    background:linear-gradient(135deg,var(--cyan),var(--blue));transform:rotate(-6deg);
    box-shadow:6px 6px 0 rgba(236,72,153,.25), 0 10px 24px rgba(6,182,212,.4)}
  .title{font-family:'Bungee';font-size:clamp(30px,8vw,44px);line-height:.98;letter-spacing:.5px}
  .title .w{display:inline-block;margin:0 2px}
  .title span{display:inline-block;-webkit-text-stroke:1.5px #fff;paint-order:stroke fill}
  .c1{color:var(--cyan);text-shadow:3px 3px 0 rgba(6,182,212,.22)}
  .c2{color:var(--blue);text-shadow:3px 3px 0 rgba(37,99,235,.22)}
  .c3{color:var(--violet);text-shadow:3px 3px 0 rgba(139,92,246,.22)}
  .c4{color:var(--pink);text-shadow:3px 3px 0 rgba(236,72,153,.22)}
  .c5{color:var(--amber);text-shadow:3px 3px 0 rgba(245,158,11,.24)}
  .sub{margin-top:14px;font-weight:700;font-size:13px;color:#7a89a8;letter-spacing:.02em}
  .pin{margin:26px 0 4px;width:100%;text-align:center;letter-spacing:.55em;font-family:'JetBrains Mono',monospace;
    font-size:26px;font-weight:700;color:var(--ink);background:#f4f8fd;border:2px solid #e3ebf6;border-radius:14px;
    padding:16px 10px;outline:none;box-shadow:5px 5px 0 rgba(37,99,235,.10);transition:.16s}
  .pin::placeholder{letter-spacing:.35em;color:#c2cde0}
  .pin:focus{border-color:var(--blue);box-shadow:5px 5px 0 rgba(6,182,212,.22)}
  .card.err .pin{border-color:var(--pink);box-shadow:5px 5px 0 rgba(236,72,153,.28);animation:shake .35s}
  @keyframes shake{0%,100%{transform:translateX(0)}25%{transform:translateX(-7px)}75%{transform:translateX(7px)}}
  .btn{margin-top:16px;width:100%;padding:15px;border:none;border-radius:14px;cursor:pointer;
    font-family:'Bungee';font-size:15px;letter-spacing:.5px;color:#fff;
    background:linear-gradient(120deg,var(--cyan),var(--blue));
    box-shadow:5px 5px 0 rgba(236,72,153,.30), 0 10px 22px rgba(37,99,235,.28);transition:.16s}
  .btn:hover{transform:translate(-1px,-1px);box-shadow:7px 7px 0 rgba(236,72,153,.32),0 14px 26px rgba(37,99,235,.3)}
  .btn:active{transform:translate(2px,2px);box-shadow:2px 2px 0 rgba(236,72,153,.3)}
  .btn:disabled{opacity:.6;cursor:wait}
  .msg{height:18px;font-size:12px;font-weight:700;color:var(--pink);margin-top:12px;font-family:'JetBrains Mono',monospace}
  @media(prefers-reduced-motion:reduce){.sticker{opacity:.1}}
</style>
</head>
<body>
  <div class="sticker s1">★</div><div class="sticker s2">✦</div><div class="sticker s3">✷</div><div class="sticker s4">◆</div>
  <form class="card" id="gate" autocomplete="off">
    <div class="logo">
      <svg width="34" height="34" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <rect x="2.5" y="7.5" width="19" height="12.5" rx="2.5"/><path d="M8 7.5V6a2.5 2.5 0 0 1 2.5-2.5h3A2.5 2.5 0 0 1 16 6v1.5"/><path d="M2.5 12.5h19"/><path d="M12 11.5v2"/>
      </svg>
    </div>
    <div class="title">
      <span class="w"><span class="c1">T</span><span class="c2">H</span><span class="c3">E</span></span>
      <span class="w"><span class="c4">J</span><span class="c5">O</span><span class="c1">B</span></span>
      <span class="w"><span class="c2">H</span><span class="c3">U</span><span class="c4">N</span><span class="c5">T</span></span>
    </div>
    <div class="sub">drop the PIN to unlock the radar</div>
    <input class="pin" id="pin" inputmode="numeric" autocomplete="off" placeholder="••••" autofocus />
    <button class="btn" id="go" type="submit">Unlock</button>
    <div class="msg" id="msg"></div>
  </form>

<script id="payload" type="application/json">${payloadJson}</script>
<script>
  const P = JSON.parse(document.getElementById("payload").textContent);
  const b64 = s => Uint8Array.from(atob(s), c => c.charCodeAt(0));
  async function decrypt(pin){
    const salt=b64(P.salt), iv=b64(P.iv), ct=b64(P.ct);
    const mat=await crypto.subtle.importKey("raw", new TextEncoder().encode(pin), "PBKDF2", false, ["deriveKey"]);
    const key=await crypto.subtle.deriveKey({name:"PBKDF2",salt,iterations:P.iterations,hash:"SHA-256"},mat,{name:"AES-GCM",length:256},false,["decrypt"]);
    const pt=await crypto.subtle.decrypt({name:"AES-GCM",iv},key,ct);
    return new TextDecoder().decode(pt);
  }
  const form=document.getElementById("gate"),inp=document.getElementById("pin"),btn=document.getElementById("go"),msg=document.getElementById("msg");
  const cryptoBlocked=()=>!window.isSecureContext||!(window.crypto&&crypto.subtle);
  if(cryptoBlocked()){msg.innerHTML="Open the <b>https://</b> address";}
  form.addEventListener("submit", async e=>{
    e.preventDefault();
    if(cryptoBlocked()){form.classList.add("err");msg.innerHTML="Needs the <b>https://</b> address — not a local file";setTimeout(()=>form.classList.remove("err"),400);return;}
    const pin=inp.value.replace(/\\s+/g,"");
    if(!pin)return;
    btn.disabled=true;msg.textContent="checking…";
    try{const html=await decrypt(pin);document.open();document.write(html);document.close();}
    catch(err){form.classList.add("err");msg.textContent="Wrong PIN";btn.disabled=false;inp.value="";inp.focus();setTimeout(()=>form.classList.remove("err"),400);}
  });
</script>
</body>
</html>`;
}
