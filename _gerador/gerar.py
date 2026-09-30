# Gera as landing pages estáticas da EcoClima a partir de dados.py.
# Uso: python _gerador/gerar.py   (rodar da raiz do projeto ou de qualquer lugar)
#
# DOMINIO: preencher quando o domínio personalizado estiver definido
# (ex.: "https://www.ecoclimajp.com.br"). Enquanto vazio, as páginas saem
# sem canonical/og:url e o sitemap.xml não é gerado — melhor sem canonical
# do que com canonical apontando para o endereço errado.
import json, os, html
from dados import EMPRESA as E, PAGINAS

DOMINIO = ""

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
esc = html.escape

# ---------- ícones (SVG inline, sem biblioteca) ----------
def ico(nome, cls="ico"):
    p = {
        "wa": '<path d="M12 2a10 10 0 0 0-8.6 15.1L2 22l5-1.3A10 10 0 1 0 12 2Zm0 18.2a8.2 8.2 0 0 1-4.2-1.2l-.3-.2-3 .8.8-2.9-.2-.3A8.2 8.2 0 1 1 12 20.2Zm4.5-6.1c-.2-.1-1.5-.7-1.7-.8-.2-.1-.4-.1-.6.1l-.8 1c-.1.2-.3.2-.5.1a6.7 6.7 0 0 1-3.3-2.9c-.3-.4.3-.4.7-1.4.1-.2 0-.3 0-.4l-.8-1.8c-.2-.5-.4-.4-.6-.4h-.5a1 1 0 0 0-.7.3 3 3 0 0 0-.9 2.2 5.2 5.2 0 0 0 1.1 2.7 11.8 11.8 0 0 0 4.5 4c1.7.7 2.3.8 3.2.6.5-.1 1.5-.6 1.7-1.2.2-.6.2-1.1.2-1.2l-.5-.3Z" fill="currentColor" stroke="none"/>',
        "x": '<path d="M18 6 6 18M6 6l12 12"/>',
        "check": '<circle cx="12" cy="12" r="9"/><path d="m8.5 12 2.5 2.5 4.5-5"/>',
        "shield": '<path d="M12 3 4.5 6v5.5c0 4.6 3.2 8.4 7.5 9.5 4.3-1.1 7.5-4.9 7.5-9.5V6L12 3Z"/>',
        "star": '<path d="m12 3 2.7 5.6 6.1.9-4.4 4.3 1 6.1L12 17l-5.4 2.9 1-6.1L3.2 9.5l6.1-.9L12 3Z" fill="currentColor"/>',
        "alert": '<path d="M12 4 2.5 20h19L12 4Z"/><path d="M12 10v4M12 17h.01"/>',
        "bolt": '<path d="M13 2 4 14h7l-1 8 9-12h-7l1-8Z"/>',
        "award": '<circle cx="12" cy="9" r="6"/><path d="m8.5 14-1.5 8 5-3 5 3-1.5-8"/>',
        "clock": '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>',
        "thumb": '<path d="M7 10v11H3V10h4Zm0 0 4-8a3 3 0 0 1 3 3v4h5.5a2 2 0 0 1 2 2.3l-1.4 8A2 2 0 0 1 18 21H7"/>',
        "pin": '<path d="M12 21s-7-6.2-7-11.5a7 7 0 0 1 14 0C19 14.8 12 21 12 21Z"/><circle cx="12" cy="9.5" r="2.5"/>',
        "phone": '<path d="M21 16.5v3a2 2 0 0 1-2.2 2A19 19 0 0 1 2.5 5.2 2 2 0 0 1 4.5 3h3a2 2 0 0 1 2 1.7c.1 1 .4 1.9.7 2.8a2 2 0 0 1-.5 2.1L8.4 10.9a16 16 0 0 0 4.7 4.7l1.3-1.3a2 2 0 0 1 2.1-.5c.9.3 1.8.6 2.8.7a2 2 0 0 1 1.7 2Z"/>',
        "chev": '<path d="m6 9 6 6 6-6"/>',
        "arrow": '<path d="M5 12h14M13 6l6 6-6 6"/>',
    }[nome]
    return f'<svg class="{cls}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{p}</svg>'

CSS = """
:root{--g:#149541;--g2:#0f7a35;--gl:#e3f2e8;--mint:#ecf4ef;--bg:#f6f7f5;--ink:#0a0a0a;--mut:#666;--card:#fff;--line:#dcefe2;--dk:#000;--dk2:#0d0d0d;--dkline:#1f1f1f;--r:14px;
--fh:'Sora',system-ui,sans-serif;--fb:'Manrope',system-ui,sans-serif}
*{box-sizing:border-box;margin:0;padding:0}
html{scroll-behavior:smooth;-webkit-text-size-adjust:100%}
body{font-family:var(--fb);color:var(--ink);background:var(--bg);line-height:1.6;font-size:16px;overflow-x:hidden}
img{max-width:100%;display:block;height:auto}
a{color:inherit;text-decoration:none}
.ico{width:1.25em;height:1.25em;flex:none}
.wrap{width:100%;max-width:1140px;margin:0 auto;padding:0 20px}
h1,h2,h3{font-family:var(--fh);line-height:1.15;letter-spacing:-.02em}
section{padding:72px 0}
.eyebrow{display:flex;align-items:center;justify-content:center;gap:12px;color:var(--g);font-size:.78rem;letter-spacing:.14em;text-transform:uppercase;font-weight:600;margin-bottom:14px}
.eyebrow:before,.eyebrow:after{content:"";height:1px;width:48px;background:currentColor;opacity:.6}
.h2{font-size:clamp(1.75rem,5.5vw,2.6rem);font-weight:700;text-align:center;margin-bottom:40px}
.btn{display:inline-flex;align-items:center;justify-content:center;gap:10px;font-weight:700;font-size:1.05rem;border-radius:12px;padding:16px 28px;transition:transform .15s,background .15s;min-height:52px}
.btn:hover{transform:translateY(-1px)}
.btn-g{background:var(--g);color:#fff;box-shadow:0 10px 30px -10px rgba(20,149,65,.6)}
.btn-g:hover{background:var(--g2)}
.btn-o{border:1px solid rgba(20,149,65,.45);color:var(--g)}
.dark{background:var(--dk);color:#f5f5f5}
/* topo */
.top{position:absolute;inset:0 0 auto;z-index:5;padding:18px 0}
.top .wrap{display:flex;align-items:center;justify-content:space-between}
.logo img{width:48px;height:auto}
.top .btn{padding:10px 16px;min-height:42px;font-size:.95rem;border-radius:10px}
/* hero */
.hero{position:relative;padding:130px 0 64px;overflow:hidden;background:radial-gradient(circle at 85% 20%,rgba(20,149,65,.14),transparent 45%),var(--dk)}
.hero:before{content:"";position:absolute;right:-180px;top:40px;width:560px;height:560px;border:1px solid #161616;border-radius:50%;box-shadow:0 0 0 90px transparent,inset 0 0 0 90px transparent}
.hero-grid{position:relative;display:grid;gap:44px;align-items:center}
.hero .eyebrow{justify-content:flex-start}
.hero .eyebrow:after{display:none}
.hero h1{font-size:clamp(2rem,8.4vw,3.4rem);font-weight:700;color:#fff;margin-bottom:18px}
.hero .sub{color:#b9b9b9;font-size:1.08rem;margin-bottom:22px;max-width:560px}
.proof{display:flex;align-items:center;gap:10px;color:#ddd;font-size:.92rem;margin-bottom:8px}
.stars{display:flex;gap:3px;color:var(--g)}
.stars .ico{width:18px;height:18px}
.garant{display:flex;align-items:center;gap:8px;color:#ddd;font-size:.9rem;margin-bottom:28px}
.garant .ico{color:var(--g);width:16px;height:16px}
.ctas{display:flex;flex-direction:column;gap:12px;max-width:340px}
.ctas small{color:#8a8a8a;font-size:.8rem;margin-top:4px}
.hero-img{position:relative;max-width:520px;width:100%;justify-self:center}
.hero-img img{border-radius:20px;width:100%;aspect-ratio:4/3;object-fit:cover;object-position:50% 30%}
.badge{position:absolute;left:-4px;bottom:-18px;background:var(--g);color:#fff;border-radius:12px;padding:12px 20px;box-shadow:0 14px 30px -10px rgba(0,0,0,.6)}
.badge span{display:block;font-size:.72rem;letter-spacing:.1em;text-transform:uppercase;opacity:.9}
.badge b{font-family:var(--fh);font-size:1.05rem}
/* dores */
.pill{display:flex;align-items:center;justify-content:center;gap:8px;max-width:340px;margin:0 auto 16px;background:#f7e1e1;color:#c0392b;border-radius:999px;padding:6px 16px;font-size:.74rem;letter-spacing:.1em;text-transform:uppercase;font-weight:600;text-align:center}
.pill .ico{width:15px;height:15px}
.list{display:grid;gap:16px;max-width:820px;margin:0 auto}
.it{display:flex;gap:14px;align-items:flex-start;background:var(--card);border:1px solid #ececec;border-radius:var(--r);padding:22px 20px;font-size:1.02rem}
.it .ico{margin-top:3px}
.pains .it .ico{color:#e5484d;width:18px;height:18px}
.center{text-align:center;margin-top:36px}
/* solução */
.dark .it{background:var(--dk2);border-color:var(--dkline);color:#eee}
.benefits .ico{color:var(--g)}
@media(min-width:760px){.list.two{grid-template-columns:1fr 1fr;max-width:1000px}}
/* sobre (seo) */
.sobre{background:var(--card)}
.sobre .txt{max-width:760px;margin:0 auto;color:#333;font-size:1.05rem}
.sobre .txt p+p{margin-top:16px}
.sobre .h2{margin-bottom:28px}
/* passos */
.steps{background:var(--mint)}
.sgrid{display:grid;gap:20px;max-width:1000px;margin:0 auto}
@media(min-width:760px){.sgrid{grid-template-columns:repeat(3,1fr)}}
.step{background:var(--card);border:1px solid #e3ece6;border-radius:18px;padding:28px}
.num{width:40px;height:40px;border-radius:50%;background:var(--g);color:#fff;display:grid;place-items:center;font-family:var(--fh);font-weight:700;margin-bottom:18px}
.step h3{font-size:1.12rem;margin-bottom:10px}
.step p{color:var(--mut)}
/* garantia */
.gbox{max-width:720px;margin:0 auto;text-align:center;background:linear-gradient(135deg,#f2f8f4,#e7f3eb);border:2px solid #b9dfc6;border-radius:22px;padding:36px 28px}
.gico{width:64px;height:64px;border-radius:50%;background:#cfe9d8;color:var(--g);display:grid;place-items:center;margin:0 auto 18px}
.gico .ico{width:28px;height:28px}
.gbox h2{font-size:1.6rem;margin-bottom:14px}
.gbox p{color:#555;font-size:1.05rem}
/* depoimentos */
.tgrid{display:grid;gap:22px;max-width:1000px;margin:0 auto}
@media(min-width:760px){.tgrid{grid-template-columns:repeat(3,1fr)}}
.tcard{background:var(--dk2);border:1px solid var(--dkline);border-radius:18px;padding:28px}
.tcard blockquote{font-style:italic;color:#ddd;margin:14px 0 20px}
.tcard b{display:block;color:#fff}
.tcard small{color:#8a8a8a}
/* selos */
.seals{padding:48px 0}
.seals .wrap{display:grid;gap:26px;text-align:center}
@media(min-width:760px){.seals .wrap{grid-template-columns:repeat(3,1fr)}}
.seal .ico{color:var(--g);width:30px;height:30px;margin:0 auto 8px}
.seal p{font-weight:600}
/* faq */
.faq{background:var(--mint)}
.faq .list{max-width:760px;gap:12px}
details{background:var(--card);border:1px solid #e3ece6;border-radius:var(--r);padding:0 20px}
summary{list-style:none;cursor:pointer;display:flex;justify-content:space-between;align-items:center;gap:14px;padding:20px 0;font-weight:600;font-size:1.02rem}
summary::-webkit-details-marker{display:none}
summary h3{font:inherit;letter-spacing:0}
summary .ico{color:var(--g);transition:transform .2s}
details[open] summary .ico{transform:rotate(180deg)}
details p{color:var(--mut);padding:0 0 20px}
/* outros serviços */
.outros{background:var(--card);padding:56px 0}
.ogrid{display:grid;gap:12px;max-width:1000px;margin:0 auto;grid-template-columns:1fr 1fr}
@media(min-width:760px){.ogrid{grid-template-columns:repeat(4,1fr)}}
.ogrid a{display:flex;align-items:center;justify-content:space-between;gap:8px;border:1px solid var(--line);border-radius:12px;padding:16px;font-weight:600;font-size:.95rem;transition:border-color .15s}
.ogrid a:hover{border-color:var(--g)}
.ogrid .ico{color:var(--g);width:18px;height:18px}
.outros .h2{font-size:1.4rem;margin-bottom:24px}
/* cta final + rodapé */
.final{text-align:center;position:relative;overflow:hidden}
.final h2{font-size:clamp(1.9rem,6vw,2.8rem);margin-bottom:16px;color:#fff}
.final p{color:#bbb;max-width:520px;margin:0 auto 28px;font-size:1.08rem}
.final small{display:block;color:#8a8a8a;margin-top:16px;font-size:.82rem}
footer{border-top:1px solid #161616;padding:48px 0 28px;text-align:center}
.fgrid{display:grid;gap:28px}
@media(min-width:760px){.fgrid{grid-template-columns:repeat(3,1fr)}}
.fgrid .ico{color:var(--g);margin:0 auto 8px}
.fgrid b{display:block;color:#fff;margin-bottom:6px}
.fgrid p,.fgrid a{color:#9a9a9a;font-size:.95rem}
.fgrid a{display:inline-flex;gap:8px;align-items:center}
.fgrid a .ico{margin:0}
.copy{color:#666;font-size:.8rem;margin-top:36px;padding-top:24px;border-top:1px solid #161616}
/* whatsapp flutuante */
.float{position:fixed;right:18px;bottom:18px;z-index:50;width:60px;height:60px;border-radius:50%;background:var(--g);color:#fff;display:grid;place-items:center;box-shadow:0 10px 30px -6px rgba(20,149,65,.7)}
.float .ico{width:32px;height:32px}
@media(min-width:960px){
 .hero{padding:150px 0 96px}
 .hero-grid{grid-template-columns:1.1fr .9fr}
 .ctas{flex-direction:row;max-width:none;flex-wrap:wrap}
 .ctas small{flex-basis:100%}
 section{padding:96px 0}
}
"""

TRACK = """<script>
document.addEventListener('click',function(e){var l=e.target&&e.target.closest?e.target.closest('a[href*="wa.me"],a[href*="api.whatsapp.com"],a[href*="crm.altusflow.com.br"]'):null;if(!l)return;window.dataLayer=window.dataLayer||[];window.dataLayer.push({event:'whatsapp_click',link_url:l.href,link_text:(l.innerText||l.getAttribute('aria-label')||'').trim().slice(0,100),page_path:window.location.pathname});},true);
(function(){var p=new URLSearchParams(window.location.search),td={gclid:p.get('gclid'),fbclid:p.get('fbclid'),gbraid:p.get('gbraid'),wbraid:p.get('wbraid'),utm_source:p.get('utm_source'),utm_medium:p.get('utm_medium'),utm_campaign:p.get('utm_campaign'),utm_term:p.get('utm_term'),utm_content:p.get('utm_content'),gad_source:p.get('gad_source'),gad_campaignid:p.get('gad_campaignid'),landing_page_url:window.location.href.split('?')[0]};
var base='%(crm)s',qp=Object.keys(td).filter(function(k){return td[k]}).map(function(k){return k+'='+encodeURIComponent(td[k])}).join('&'),url=qp?base+'?'+qp:base;
document.querySelectorAll('a[href*="/t/mumn10pv2e2k"]').forEach(function(a){a.href=url});})();
</script>"""


def rel(depth):
    return "../" * depth


def cta(txt, cls="btn btn-g", extra=""):
    return f'<a class="{cls}" href="{E["crm"]}" target="_blank" rel="noopener"{extra}>{ico("wa")}{esc(txt)}</a>'


def schema(pg, url):
    neg = {
        "@type": "HVACBusiness",
        "@id": (DOMINIO + "/#empresa") if DOMINIO else "#empresa",
        "name": E["nome"],
        "slogan": E["slogan"],
        "telephone": E["telefone_e164"],
        "address": {"@type": "PostalAddress", "streetAddress": E["rua"], "addressLocality": E["cidade"], "addressRegion": E["uf"], "addressCountry": "BR"},
        "areaServed": [{"@type": "City", "name": c} for c in ("João Pessoa", "Cabedelo", "Bayeux", "Santa Rita", "Conde")],
        "openingHoursSpecification": [{"@type": "OpeningHoursSpecification", "dayOfWeek": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"], "opens": "08:00", "closes": "18:00"}],
        "priceRange": "$$",
    }
    if DOMINIO:
        neg["url"] = DOMINIO + "/"
        neg["image"] = f"{DOMINIO}/assets/img/{pg['imagem']}-og.jpg"
        neg["logo"] = f"{DOMINIO}/assets/img/logo-ecoclima-192.webp"
    grafo = [
        neg,
        {"@type": "Service", "name": pg["servico_schema"], "serviceType": pg["servico_schema"], "description": pg["meta"], "provider": {"@id": neg["@id"]}, "areaServed": {"@type": "City", "name": "João Pessoa"}},
        {"@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in pg["faqs"]]},
    ]
    if DOMINIO:
        grafo[1]["url"] = url
        grafo.append({"@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "EcoClima", "item": DOMINIO + "/"},
            {"@type": "ListItem", "position": 2, "name": pg["servico_schema"], "item": url}]})
    return json.dumps({"@context": "https://schema.org", "@graph": grafo}, ensure_ascii=False)


def pagina(pg):
    depth = pg["slug"].count("/") + 1
    R = rel(depth)
    url = f"{DOMINIO}/{pg['slug']}/" if DOMINIO else ""
    im = pg["imagem"]
    w, h = pg["img_ratio"]
    head_url = (f'<link rel="canonical" href="{url}">\n<meta property="og:url" content="{url}">\n'
                f'<meta property="og:image" content="{DOMINIO}/assets/img/{im}-og.jpg">') if DOMINIO else f'<meta property="og:image" content="{R}assets/img/{im}-og.jpg">'

    outros = "".join(
        f'<a href="{R}{o["slug"]}/">{esc(o["servico_schema"].replace(" de ar condicionado", ""))} de ar condicionado{ico("arrow")}</a>'
        for o in PAGINAS if o["slug"] != pg["slug"])

    return f"""<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(pg['title'])}</title>
<meta name="description" content="{esc(pg['meta'])}">
<meta name="robots" content="index,follow,max-image-preview:large">
<meta name="theme-color" content="#000000">
<meta name="geo.region" content="BR-PB"><meta name="geo.placename" content="João Pessoa">
{head_url}
<meta property="og:type" content="website">
<meta property="og:locale" content="pt_BR">
<meta property="og:site_name" content="EcoClima">
<meta property="og:title" content="{esc(pg['title'])}">
<meta property="og:description" content="{esc(pg['meta'])}">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" type="image/png" href="{R}favicon.png">
<link rel="apple-touch-icon" href="{R}assets/img/apple-touch-icon.png">
<link rel="preload" as="image" type="image/webp" href="{R}assets/img/{im}-480.webp" imagesrcset="{R}assets/img/{im}-480.webp 480w, {R}assets/img/{im}-860.webp 860w" imagesizes="(min-width:960px) 520px, 100vw">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700&family=Sora:wght@600;700&display=swap" rel="stylesheet">
<style>{CSS.strip()}</style>
<script type="application/ld+json">{schema(pg, url)}</script>
<!-- Google Tag Manager -->
<script>(function(w,d,s,l,i){{w[l]=w[l]||[];w[l].push({{'gtm.start':new Date().getTime(),event:'gtm.js'}});var f=d.getElementsByTagName(s)[0],j=d.createElement(s),dl=l!='dataLayer'?'&l='+l:'';j.async=true;j.src='https://www.googletagmanager.com/gtm.js?id='+i+dl;f.parentNode.insertBefore(j,f);}})(window,document,'script','dataLayer','{E['gtm']}');</script>
</head>
<body>
<noscript><iframe src="https://www.googletagmanager.com/ns.html?id={E['gtm']}" height="0" width="0" style="display:none;visibility:hidden"></iframe></noscript>

<header class="top">
 <div class="wrap">
  <a class="logo" href="{R}" aria-label="EcoClima — página inicial"><img src="{R}assets/img/logo-ecoclima-96.webp" alt="EcoClima ar condicionado João Pessoa" width="48" height="46"></a>
  {cta("Orçamento")}
 </div>
</header>

<main>
<section class="hero">
 <div class="wrap hero-grid">
  <div>
   <p class="eyebrow">{esc(pg['tagline'])}</p>
   <h1>{esc(pg['headline'])}</h1>
   <p class="sub">{esc(pg['sub'])}</p>
   <div class="proof"><span class="stars">{ico('star')*5}</span>+30 mil atendimentos</div>
   <div class="garant">{ico('shield')}Serviço com garantia</div>
   <div class="ctas">
    {cta("Solicitar orçamento")}
    <a class="btn btn-o" href="#como-funciona">Como funciona</a>
    <small>Fale diretamente com a equipe pelo WhatsApp</small>
   </div>
  </div>
  <div class="hero-img">
   <img src="{R}assets/img/{im}-480.webp" srcset="{R}assets/img/{im}-480.webp 480w, {R}assets/img/{im}-860.webp 860w" sizes="(min-width:960px) 520px, 100vw" width="{w}" height="{h}" alt="{esc(pg['img_alt'])}" fetchpriority="high" decoding="async">
   <div class="badge"><span>Atendimento</span><b>João Pessoa e região</b></div>
  </div>
 </div>
</section>

<section class="pains">
 <div class="wrap">
  <p class="pill">{ico('alert')}Identificou algum desses problemas?</p>
  <h2 class="h2">Você não precisa conviver com isso</h2>
  <ul class="list" role="list">{''.join(f'<li class="it">{ico("x")}<span>{esc(p)}</span></li>' for p in pg['pains'])}</ul>
  <div class="center"><a class="btn btn-g" href="{E['crm']}" target="_blank" rel="noopener">{ico('bolt')}Resolver agora</a></div>
 </div>
</section>

<section class="dark benefits">
 <div class="wrap">
  <p class="eyebrow">A solução</p>
  <h2 class="h2">Por que escolher a EcoClima</h2>
  <ul class="list two" role="list">{''.join(f'<li class="it">{ico("check")}<span>{esc(b)}</span></li>' for b in pg['benefits'])}</ul>
 </div>
</section>

<section class="sobre">
 <div class="wrap">
  <p class="eyebrow">{esc(pg['nome_curto'])} em João Pessoa</p>
  <h2 class="h2">{esc(pg['sobre_titulo'])}</h2>
  <div class="txt">{''.join(f'<p>{esc(t)}</p>' for t in pg['sobre'])}</div>
 </div>
</section>

<section class="steps" id="como-funciona">
 <div class="wrap">
  <p class="eyebrow">Como funciona</p>
  <h2 class="h2">Simples, rápido e sem dor de cabeça</h2>
  <ol class="sgrid" role="list" style="list-style:none">{''.join(f'<li class="step"><div class="num">{i}</div><h3>{esc(t)}</h3><p>{esc(d)}</p></li>' for i, (t, d) in enumerate(pg['steps'], 1))}</ol>
 </div>
</section>

<section>
 <div class="wrap">
  <div class="gbox">
   <div class="gico">{ico('shield')}</div>
   <h2>Garantia EcoClima</h2>
   <p>{esc(pg['guarantee'])}</p>
  </div>
 </div>
</section>

<section class="dark">
 <div class="wrap">
  <p class="eyebrow">Quem já confiou</p>
  <h2 class="h2">Resultados reais de clientes reais</h2>
  <div class="tgrid">{''.join(f'<figure class="tcard"><span class="stars">{ico("star")*5}</span><blockquote>"{esc(t)}"</blockquote><figcaption><b>{esc(n)}</b><small>{esc(l)}</small></figcaption></figure>' for n, l, t in pg['testimonials'])}</div>
 </div>
</section>

<div class="seals">
 <div class="wrap">
  <div class="seal">{ico('award')}<p>Técnicos Autorizados</p></div>
  <div class="seal">{ico('clock')}<p>Atendimento Ágil</p></div>
  <div class="seal">{ico('thumb')}<p>+30 mil clientes satisfeitos</p></div>
 </div>
</div>

<section class="faq">
 <div class="wrap">
  <p class="eyebrow">Dúvidas frequentes</p>
  <h2 class="h2">Tudo o que você precisa saber sobre {esc(pg['keyword'])}</h2>
  <div class="list">{''.join(f'<details{" open" if i == 0 else ""}><summary><h3>{esc(q)}</h3>{ico("chev")}</summary><p>{esc(a)}</p></details>' for i, (q, a) in enumerate(pg['faqs']))}</div>
 </div>
</section>

<nav class="outros" aria-label="Outros serviços">
 <div class="wrap">
  <h2 class="h2">Outros serviços de ar condicionado em João Pessoa</h2>
  <div class="ogrid">{outros}</div>
 </div>
</nav>

<section class="dark final">
 <div class="wrap">
  <h2>Pronto para resolver de vez?</h2>
  <p>Fale agora com um especialista pelo WhatsApp e receba seu orçamento em minutos — sem compromisso.</p>
  {cta("Solicitar orçamento")}
  <small>Atendimento Seg a Sáb, das 08h às 18h</small>
 </div>
</section>
</main>

<footer class="dark">
 <div class="wrap">
  <div class="fgrid">
   <div>{ico('pin')}<b>Endereço</b><p>{esc(E['rua'])} — {esc(E['cidade'])}, {E['uf']}</p></div>
   <div>{ico('clock')}<b>Horário</b><p>{esc(E['horario'])}</p></div>
   <div>{ico('phone')}<b>Contato</b><a href="{E['crm']}" target="_blank" rel="noopener">{ico('wa')}{E['telefone']} — WhatsApp</a></div>
  </div>
  <p class="copy">© 2026 EcoClima — {esc(E['slogan'])}</p>
 </div>
</footer>

<a class="float" href="{E['crm']}" target="_blank" rel="noopener" aria-label="Falar com a EcoClima no WhatsApp">{ico('wa')}</a>
{TRACK % E}
</body>
</html>
"""


def hub():
    # Raiz do site: índice simples dos serviços (evita 404 na home e ajuda o rastreamento).
    itens = "".join(
        f'<a href="{p["slug"]}/"><b>{esc(p["servico_schema"])}</b><span>{esc(p["sub"])}</span></a>' for p in PAGINAS)
    canon = f'<link rel="canonical" href="{DOMINIO}/">' if DOMINIO else ""
    return f"""<!doctype html>
<html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Ar Condicionado em João Pessoa | EcoClima</title>
<meta name="description" content="EcoClima: instalação, manutenção, limpeza, conserto e assistência técnica de ar condicionado em João Pessoa e região, com garantia.">
{canon}<link rel="icon" type="image/png" href="favicon.png">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Manrope:wght@400;600;700&family=Sora:wght@700&display=swap" rel="stylesheet">
<style>{CSS.strip()}
.hub{{padding:120px 0 64px}}.hub h1{{color:#fff;font-size:clamp(2rem,7vw,3rem);margin-bottom:12px}}.hub .sub{{color:#bbb;margin-bottom:36px}}
.hl{{display:grid;gap:14px}}@media(min-width:760px){{.hl{{grid-template-columns:1fr 1fr}}}}
.hl a{{display:block;background:var(--dk2);border:1px solid var(--dkline);border-radius:16px;padding:22px}}.hl a:hover{{border-color:var(--g)}}
.hl b{{display:block;color:#fff;font-family:var(--fh);font-size:1.1rem;margin-bottom:6px}}.hl span{{color:#9a9a9a;font-size:.95rem}}</style>
<script>(function(w,d,s,l,i){{w[l]=w[l]||[];w[l].push({{'gtm.start':new Date().getTime(),event:'gtm.js'}});var f=d.getElementsByTagName(s)[0],j=d.createElement(s),dl=l!='dataLayer'?'&l='+l:'';j.async=true;j.src='https://www.googletagmanager.com/gtm.js?id='+i+dl;f.parentNode.insertBefore(j,f);}})(window,document,'script','dataLayer','{E['gtm']}');</script>
</head><body class="dark">
<header class="top"><div class="wrap"><a class="logo" href="./"><img src="assets/img/logo-ecoclima-96.webp" alt="EcoClima" width="48" height="46"></a>{cta("Orçamento")}</div></header>
<main class="hub"><div class="wrap"><h1>Ar condicionado em João Pessoa</h1><p class="sub">Escolha o serviço que você precisa.</p><div class="hl">{itens}</div></div></main>
<a class="float" href="{E['crm']}" target="_blank" rel="noopener" aria-label="Falar com a EcoClima no WhatsApp">{ico('wa')}</a>
{TRACK % E}
</body></html>
"""


def main():
    for pg in PAGINAS:
        d = os.path.join(RAIZ, *pg["slug"].split("/"))
        os.makedirs(d, exist_ok=True)
        with open(os.path.join(d, "index.html"), "w", encoding="utf-8", newline="\n") as f:
            f.write(pagina(pg))
        print("ok", pg["slug"])
    with open(os.path.join(RAIZ, "index.html"), "w", encoding="utf-8", newline="\n") as f:
        f.write(hub())
    robots = "User-agent: *\nAllow: /\n" + (f"Sitemap: {DOMINIO}/sitemap.xml\n" if DOMINIO else "")
    open(os.path.join(RAIZ, "robots.txt"), "w", encoding="utf-8", newline="\n").write(robots)
    if DOMINIO:
        urls = [DOMINIO + "/"] + [f"{DOMINIO}/{p['slug']}/" for p in PAGINAS]
        xml = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + \
              "".join(f"  <url><loc>{u}</loc></url>\n" for u in urls) + "</urlset>\n"
        open(os.path.join(RAIZ, "sitemap.xml"), "w", encoding="utf-8", newline="\n").write(xml)
    # GitHub Pages: sem Jekyll, para servir tudo como está
    open(os.path.join(RAIZ, ".nojekyll"), "w").close()


if __name__ == "__main__":
    main()
