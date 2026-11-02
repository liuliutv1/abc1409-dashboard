# -*- coding: utf-8 -*-
"""抓取农银匠心·灵动14天第9期G 净值，生成手机优先的静态看板。

在 GitHub Actions 上运行（Linux，无第三方依赖），也可本地直接运行。
输出：docs/index.html
"""
import json
import ssl
import urllib.request
from datetime import datetime, timezone, timedelta
from pathlib import Path

API = "https://www.abcwealth.com.cn/awpsservice/fpproduct/productyield/findNetOr7DaysList"
CODE = "NYJXLD1409G"
NAME = "农银匠心灵动14天 第9期 G"
WINDOW = 90
OUT = Path(__file__).resolve().parent / "docs" / "index.html"

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/120.0 Safari/537.36")


def post_json(url: str) -> dict:
    # 农银服务器不支持 RFC5746 安全重协商，需放开 legacy renegotiation
    ctx = ssl.create_default_context()
    ctx.options |= getattr(ssl, "OP_LEGACY_SERVER_CONNECT", 0x00040000)
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    req = urllib.request.Request(
        url, data=b"{}", method="POST",
        headers={"Content-Type": "application/json", "User-Agent": UA,
                 "Referer": "https://www.abcwealth.com.cn/"})
    with urllib.request.urlopen(req, timeout=30, context=ctx) as r:
        return json.loads(r.read().decode("utf-8"))


def fetch_navs() -> list[dict]:
    rows, page = [], 1
    while True:
        data = post_json(f"{API}?productId={CODE}&type=NET&current={page}").get("data") or {}
        recs = data.get("records") or []
        for x in recs:
            try:
                rows.append({"date": str(x.get("dateNet")),
                             "unit": float(x.get("vluUnitNet"))})
            except (TypeError, ValueError):
                continue
        pages = data.get("pages") or 1
        if page >= pages or not recs or page >= 40:
            break
        page += 1
    rows.sort(key=lambda x: x["date"])
    # 去重（同日期保留最后一条）
    dedup: dict[str, dict] = {}
    for r in rows:
        dedup[r["date"]] = r
    return [dedup[k] for k in sorted(dedup)]


def build(navs: list[dict]) -> dict:
    recent = navs[-WINDOW:]
    daily = []
    for i, r in enumerate(recent):
        wan = round((r["unit"] - recent[i - 1]["unit"]) * 10000, 2) if i else None
        daily.append({"d": r["date"], "nav": round(r["unit"], 6), "wan": wan})

    latest = daily[-1]
    bj = datetime.now(timezone.utc) + timedelta(hours=8)
    today = bj.strftime("%Y%m%d")
    gap = (datetime.strptime(today, "%Y%m%d") - datetime.strptime(latest["d"], "%Y%m%d")).days

    def sum_wan(n: int) -> float:
        return round(sum(x["wan"] for x in daily[-n:] if x["wan"] is not None), 2)

    return {
        "code": CODE, "name": NAME,
        "latest_date": latest["d"],
        "latest_nav": latest["nav"],
        "latest_wan": latest["wan"],
        "fresh": gap <= 1,
        "built_at": bj.strftime("%Y-%m-%d %H:%M"),
        "daily": daily,
        "w7": sum_wan(7), "w30": sum_wan(30), "wall": sum_wan(len(daily)),
        "min_wan": min((x["wan"] for x in daily if x["wan"] is not None), default=0),
        "max_wan": max((x["wan"] for x in daily if x["wan"] is not None), default=0),
        "down_days": sum(1 for x in daily if x["wan"] is not None and x["wan"] < 0),
    }


TPL = r"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="theme-color" content="#0a0c11">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="mobile-web-app-capable" content="yes">
<title>__NAME__</title>
<style>
*{margin:0;padding:0;box-sizing:border-box;-webkit-tap-highlight-color:transparent}
:root{--bg:#0a0c11;--card:#13171f;--line:#1e2430;--txt:#e8eaf0;--dim:#7b8496;--dimmer:#4e5666;--blue:#5b8def;--up:#f6465d;--down:#0ecb81}
html{-webkit-text-size-adjust:100%}
body{font-family:-apple-system,BlinkMacSystemFont,"PingFang SC","Microsoft YaHei",system-ui,sans-serif;
background:var(--bg);color:var(--txt);font-size:15px;line-height:1.5;
padding:calc(env(safe-area-inset-top) + 16px) 14px calc(env(safe-area-inset-bottom) + 32px);
max-width:560px;margin:0 auto;-webkit-font-smoothing:antialiased}
.hd{display:flex;justify-content:space-between;align-items:flex-start;gap:10px;margin-bottom:18px}
.hd h1{font-size:15px;font-weight:600;letter-spacing:-.01em;line-height:1.3}
.hd .sub{font-size:11px;color:var(--dimmer);margin-top:4px;font-variant-numeric:tabular-nums}
.badge{font-size:11px;padding:4px 10px;border-radius:999px;font-weight:600;white-space:nowrap;flex-shrink:0}
.badge.ok{background:rgba(34,197,94,.13);color:#4ade80}
.badge.wait{background:rgba(234,179,8,.13);color:#facc15}
.hero{background:var(--card);border:1px solid var(--line);border-radius:18px;padding:22px 20px;margin-bottom:12px}
.hero .lbl{font-size:11px;color:var(--dim);letter-spacing:.05em;margin-bottom:10px}
.hero .big{font-size:44px;font-weight:680;letter-spacing:-.03em;font-variant-numeric:tabular-nums;line-height:1.05}
.hero .date{font-size:12px;color:var(--dimmer);margin-top:8px;font-variant-numeric:tabular-nums}
.hero .wan{margin-top:16px;padding-top:16px;border-top:1px solid var(--line);display:flex;align-items:baseline;gap:8px}
.hero .wan .num{font-size:26px;font-weight:650;font-variant-numeric:tabular-nums;letter-spacing:-.02em}
.hero .wan .u{font-size:13px;color:var(--dim)}
.hero .wan .tag{font-size:11px;color:var(--dim);margin-left:auto}
.grid{display:grid;grid-template-columns:repeat(3,1fr);gap:8px;margin-bottom:12px}
.g{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:13px 12px}
.g .k{font-size:10px;color:var(--dimmer);letter-spacing:.04em;margin-bottom:7px}
.g .v{font-size:17px;font-weight:640;font-variant-numeric:tabular-nums;letter-spacing:-.01em}
section{background:var(--card);border:1px solid var(--line);border-radius:16px;padding:16px 14px;margin-bottom:12px}
section h2{font-size:12px;font-weight:600;color:#9aa3b5;letter-spacing:.04em;margin-bottom:14px;display:flex;justify-content:space-between;align-items:center}
section h2 span{font-size:10px;font-weight:400;color:var(--dimmer);letter-spacing:0}
svg{display:block;width:100%;height:auto}
.row{display:flex;align-items:center;padding:11px 2px;border-bottom:1px solid #161b23;font-variant-numeric:tabular-nums;font-size:13.5px}
.row:last-child{border-bottom:none}
.row .d{color:var(--dim);width:62px;flex-shrink:0;font-size:12.5px}
.row .n{color:#c3cadd;flex:1;font-size:12.5px}
.row .w{width:86px;text-align:right;font-weight:600}
.up{color:var(--up)}.down{color:var(--down)}.flat{color:#6b7486}
.scroll{max-height:46vh;overflow-y:auto;-webkit-overflow-scrolling:touch}
.scroll::-webkit-scrollbar{width:0}
footer{text-align:center;font-size:10.5px;color:#3a4150;margin-top:22px;line-height:1.9}
.tip{font-size:11px;color:var(--dimmer);margin-top:10px;line-height:1.6}
</style>
</head>
<body>
<div class="hd">
  <div><h1>__NAME__</h1><div class="sub">__CODE__</div></div>
  <div id="badge"></div>
</div>
<div class="hero">
  <div class="lbl">最新单位净值</div>
  <div class="big" id="nav">—</div>
  <div class="date" id="ndate">—</div>
  <div class="wan"><span class="num" id="wan">—</span><span class="u">元 / 万份</span><span class="tag" id="wtxt"></span></div>
</div>
<div class="grid">
  <div class="g"><div class="k">近 7 天</div><div class="v" id="g7">—</div></div>
  <div class="g"><div class="k">近 30 天</div><div class="v" id="g30">—</div></div>
  <div class="g"><div class="k">近 __N__ 天</div><div class="v" id="gall">—</div></div>
</div>
<section><h2>单位净值走势<span id="navrng"></span></h2><svg id="c1" viewBox="0 0 340 168"></svg></section>
<section><h2>每日万份收益<span>红涨 绿跌</span></h2><svg id="c2" viewBox="0 0 340 140"></svg><div class="tip" id="insight"></div></section>
<section><h2>净值明细<span id="cnt"></span></h2><div class="scroll"><div id="rows"></div></div></section>
<footer>数据来源 农银理财官网 · 渲染于 __BUILT__（北京时间）<br>每万份收益 = 相邻净值差 × 10000</footer>
<script>
const DATA = __DATA__;
function fmt(d){return d.slice(4,6)+'-'+d.slice(6,8);}
function full(d){return d.slice(0,4)+'-'+d.slice(4,6)+'-'+d.slice(6,8);}
function sign(v){return (v>0?'+':'')+v.toFixed(2);}
function cls(v){return v>0?'up':(v<0?'down':'flat');}
(function(){
  const D=DATA;
  document.getElementById('badge').innerHTML = D.fresh
    ? '<span class="badge ok">已更新</span>'
    : '<span class="badge wait">待更新</span>';
  document.getElementById('nav').textContent = D.latest_nav.toFixed(6);
  document.getElementById('ndate').textContent = full(D.latest_date) + (D.fresh?'':' · 今日未披露');
  const w=D.latest_wan, we=document.getElementById('wan');
  we.textContent = w===null?'—':sign(w);
  we.className='num '+(w===null?'flat':cls(w));
  document.getElementById('wtxt').textContent = w===null?'':(w>0?'↑ 上涨':(w<0?'↓ 下跌':'持平'));
  [['g7',D.w7],['g30',D.w30],['gall',D.wall]].forEach(([id,v])=>{
    const e=document.getElementById(id); e.textContent=sign(v); e.className='v '+cls(v);
  });
  document.getElementById('cnt').textContent = D.daily.length+' 个净值日';
  document.getElementById('insight').textContent =
    '区间最大单日 +'+D.max_wan.toFixed(2)+' 元，最大单日 '+D.min_wan.toFixed(2)+
    ' 元；'+D.daily.length+' 天中 '+D.down_days+' 天下跌。';

  // 净值折线
  (function(){
    const d=D.daily,W=340,H=168,PL=4,PR=4,PT=14,PB=18;
    const vals=d.map(x=>x.nav); let lo=Math.min(...vals),hi=Math.max(...vals);
    const pad=(hi-lo)*0.18||0.0008; lo-=pad; hi+=pad;
    const X=i=>PL+i*(W-PL-PR)/Math.max(d.length-1,1);
    const Y=v=>PT+(hi-v)*(H-PT-PB)/(hi-lo);
    let line='';
    d.forEach((p,i)=>{line+=(i?'L':'M')+X(i).toFixed(1)+','+Y(p.nav).toFixed(1);});
    const area=line+'L'+X(d.length-1).toFixed(1)+','+(H-PB)+'L'+X(0).toFixed(1)+','+(H-PB)+'Z';
    let grid='';
    for(let g=0;g<=2;g++){const y=PT+g*(H-PT-PB)/2;
      grid+='<line x1="0" y1="'+y.toFixed(1)+'" x2="'+W+'" y2="'+y.toFixed(1)+'" stroke="#1b2029" stroke-width="1"/>';}
    const li=d.length-1;
    document.getElementById('c1').innerHTML=
      '<defs><linearGradient id="ga" x1="0" y1="0" x2="0" y2="1">'+
      '<stop offset="0%" stop-color="#5b8def" stop-opacity="0.3"/>'+
      '<stop offset="100%" stop-color="#5b8def" stop-opacity="0"/></linearGradient></defs>'+
      grid+'<path d="'+area+'" fill="url(#ga)"/>'+
      '<path d="'+line+'" fill="none" stroke="#5b8def" stroke-width="2" stroke-linejoin="round" stroke-linecap="round"/>'+
      '<circle cx="'+X(li).toFixed(1)+'" cy="'+Y(d[li].nav).toFixed(1)+'" r="3.5" fill="#5b8def" stroke="#13171f" stroke-width="2"/>';
    document.getElementById('navrng').textContent=lo.toFixed(4)+' ~ '+hi.toFixed(4);
  })();

  // 万收柱状
  (function(){
    const s=D.daily.filter(x=>x.wan!==null);
    if(!s.length)return;
    const W=340,H=140,PT=10,PB=8,PL=2,PR=2;
    const mx=Math.max(...s.map(x=>Math.abs(x.wan)),1);
    const zero=PT+(H-PT-PB)/2, sc=(H-PT-PB)/2/mx;
    const bw=Math.max(1.6,(W-PL-PR)/s.length-1.1);
    let bars='';
    s.forEach((p,i)=>{
      const x=PL+i*(W-PL-PR)/s.length+0.55;
      const h=Math.abs(p.wan)*sc, y=p.wan>=0?zero-h:zero;
      const c=p.wan>0?'#f6465d':(p.wan<0?'#0ecb81':'#2a3140');
      bars+='<rect x="'+x.toFixed(1)+'" y="'+y.toFixed(1)+'" width="'+bw.toFixed(1)+
            '" height="'+Math.max(h,0.9).toFixed(1)+'" fill="'+c+'" rx="0.8"/>';
    });
    document.getElementById('c2').innerHTML=
      '<line x1="0" y1="'+zero.toFixed(1)+'" x2="'+W+'" y2="'+zero.toFixed(1)+'" stroke="#242b38" stroke-width="1"/>'+bars;
  })();

  // 明细
  (function(){
    const d=D.daily; let h='';
    for(let i=d.length-1;i>=0;i--){
      const p=d[i];
      const w=p.wan===null?'—':sign(p.wan);
      const c=p.wan===null?'flat':cls(p.wan);
      h+='<div class="row"><span class="d">'+fmt(p.d)+'</span><span class="n">'+
         p.nav.toFixed(6)+'</span><span class="w '+c+'">'+w+'</span></div>';
    }
    document.getElementById('rows').innerHTML=h;
  })();
})();
</script>
</body>
</html>
"""


def main() -> None:
    navs = fetch_navs()
    if not navs:
        raise SystemExit("抓取失败：未取得任何净值记录")
    d = build(navs)
    html = (TPL.replace("__NAME__", d["name"])
               .replace("__CODE__", d["code"])
               .replace("__N__", str(len(d["daily"])))
               .replace("__BUILT__", d["built_at"])
               .replace("__DATA__", json.dumps(d, ensure_ascii=False)))
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(html, encoding="utf-8")
    print(f"OK 最新 {d['latest_date']} 净值 {d['latest_nav']:.6f} "
          f"万收 {d['latest_wan']:+.2f} {'已更新' if d['fresh'] else '待更新'} "
          f"→ {OUT}")


if __name__ == "__main__":
    main()
