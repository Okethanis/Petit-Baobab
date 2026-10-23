"""23 oct. 2026 — inspiré de Keraby, à l'identité Petit Baobab :
   1. Titres en Fraunces (serif douce), texte en Nunito Sans ; logo et prix en Fredoka.
   2. Deux boutons ronds empilés en bas à droite : WhatsApp (vert) au-dessus, Appeler (soleil) en dessous,
      avec une bulle d'aide au survol sur ordinateur.
   3. L'ambiance (brand/ambiance.css + brand/ambiance.js) : bloc CSS balisé dans le style principal, script à la fin.
   Idempotent : relancer ne duplique rien."""
import os, re
HERE = os.path.dirname(os.path.abspath(__file__))
P = os.path.join(HERE, '..', 'petit-baobab.html')
s = open(P, encoding='utf-8').read()

def rep(old, new, count=1):
    global s
    n = s.count(old)
    if n == 0 and s.count(new) >= 1: return          # déjà fait
    assert n == count, (n, old[:80]); s = s.replace(old, new)

# ---------- 1. polices (réglées par expression régulière : le résultat ne dépend pas de l'état de départ) ----------
FONTS = ('<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght,SOFT@9..144,500..700,100'
         '&family=Fredoka:wght@500;600;700&family=Nunito+Sans:ital,wght@0,400;0,600;0,700;1,400&display=swap">')
s = re.sub(r'<link rel="stylesheet" href="https://fonts\.googleapis\.com/css2\?[^"]*">', lambda m: FONTS, s, count=1)
s = re.sub(r'(  --font-brand:[^\n]*\n)?  --font-display:[^\n]*\n  --font-body:[^\n]*', lambda m:
           '  --font-brand:"Fredoka","Trebuchet MS",system-ui,sans-serif;\n'
           '  --font-display:"Fraunces",Georgia,"Times New Roman",serif;\n'
           '  --font-body:"Nunito Sans","Segoe UI",system-ui,sans-serif;', s, count=1)
s = re.sub(r'h1,h2,h3,h4\{font-family:var\(--font-display\);[^}]*\}', lambda m:
           'h1,h2,h3,h4{font-family:var(--font-display);font-weight:600;line-height:1.1;margin:0;text-wrap:balance;letter-spacing:-.005em;font-optical-sizing:auto;font-variant-numeric:lining-nums}', s, count=1)
rep('.logo{display:inline-flex;align-items:center;gap:10px;text-decoration:none;font-family:var(--font-display);',
    '.logo{display:inline-flex;align-items:center;gap:10px;text-decoration:none;font-family:var(--font-brand);')
rep('.pb-logo .word{font-family:var(--font-display);', '.pb-logo .word{font-family:var(--font-brand);')
rep('.wink h3{font-family:var(--font-display);', '.wink h3{font-family:var(--font-brand);')

# ---------- 2. boutons flottants ----------
rep('<a class="fab fab-wa" id="fab-wa" href="#" target="_blank" rel="noopener" aria-label="Nous écrire sur WhatsApp"><svg class="icon"><use href="#i-chat"/></svg><span>WhatsApp</span></a>',
    '<a class="fab fab-wa" id="fab-wa" href="#" target="_blank" rel="noopener" aria-label="Nous écrire sur WhatsApp"><svg class="icon"><use href="#i-wa"/></svg><span class="fab-tip">Écrire sur WhatsApp</span></a>\n'
    '  <a class="fab fab-call" id="fab-call" href="tel:+2250768211934" aria-label="Nous appeler"><svg class="icon"><use href="#i-phone"/></svg><span class="fab-tip">Appeler le <span class="wa-num">+225 07 68 21 19 34</span></span></a>')
rep("  $('#fab-wa').href = waLink('Bonjour ' + CONFIG.brand + ', j\\'ai une question.');",
    "  $('#fab-wa').href = waLink('Bonjour ' + CONFIG.brand + ', j\\'ai une question.');\n  $('#fab-call').href = 'tel:+' + CONFIG.whatsapp;")
# icônes : WhatsApp (pictogramme plein) et téléphone (plein)
rep('<symbol id="i-chat" viewBox="0 0 24 24">',
    '<symbol id="i-wa" viewBox="0 0 24 24"><path fill="currentColor" stroke="none" d="M12 2.2a9.7 9.7 0 0 0-8.3 14.8L2.4 21.6l4.7-1.2A9.7 9.7 0 1 0 12 2.2zm0 17.7a8 8 0 0 1-4.1-1.1l-.3-.2-2.8.7.8-2.7-.2-.3A8 8 0 1 1 12 19.9zm4.4-6c-.2-.1-1.4-.7-1.7-.8-.2-.1-.4-.1-.5.1l-.8 1c-.1.2-.3.2-.5.1a6.6 6.6 0 0 1-3.3-2.9c-.2-.4.2-.4.7-1.3.1-.2 0-.3 0-.4l-.8-1.8c-.2-.5-.4-.4-.5-.4h-.5a.9.9 0 0 0-.7.3 2.8 2.8 0 0 0-.9 2.1 4.9 4.9 0 0 0 1 2.6 11.2 11.2 0 0 0 4.3 3.8c1.6.7 2.2.7 3 .6a2.6 2.6 0 0 0 1.7-1.2 2.1 2.1 0 0 0 .2-1.2c-.1-.1-.2-.2-.4-.3z"/></symbol>'
    '<symbol id="i-phone" viewBox="0 0 24 24"><path fill="currentColor" stroke="none" d="M6.6 3.2c.5-.4 1.2-.3 1.6.2l2.3 3c.4.5.3 1.2-.1 1.6L9 9.3c-.3.3-.4.7-.2 1.1a12.4 12.4 0 0 0 4.8 4.8c.4.2.8.1 1.1-.2l1.3-1.4c.4-.4 1.1-.5 1.6-.1l3 2.3c.5.4.6 1.1.2 1.6l-1.5 2c-.6.8-1.6 1.2-2.6 1A17.6 17.6 0 0 1 3.6 7.3c-.2-1 .2-2 1-2.6z"/></symbol>'
    '<symbol id="i-chat" viewBox="0 0 24 24">')
# style des boutons
rep('.fab-wa span{display:none}\n@media(min-width:860px){.fab-wa{padding:0 18px 0 14px}.fab-wa span{display:inline}}\n',
    '.fab-wa,.fab-call{position:relative;width:58px;height:58px;min-height:0;padding:0;justify-content:center;border-radius:50%}\n'
    '.fab-wa .icon,.fab-call .icon{width:29px;height:29px}\n'
    '.fab-call{background:var(--accent);color:var(--accent-ink)}\n'
    '.fab-tip{position:absolute;right:calc(100% + 12px);top:50%;transform:translate(10px,-50%);opacity:0;white-space:nowrap;background:var(--surface);color:var(--ink);font-size:.86rem;font-weight:600;padding:8px 14px;border-radius:999px;box-shadow:var(--shadow);border:1px solid var(--line);pointer-events:none;transition:opacity .2s,transform .35s var(--spring)}\n'
    '@media (hover:hover){.fab-wa:hover .fab-tip,.fab-call:hover .fab-tip{opacity:1;transform:translate(0,-50%)}}\n'
    '.fab:focus-visible .fab-tip{opacity:1;transform:translate(0,-50%)}\n'
    '.fab-wa::after,.fab-call::after{content:"";position:absolute;inset:0;border-radius:50%;pointer-events:none}\n'
    '@media (prefers-reduced-motion: no-preference){\n'
    '  .fab-wa::after{animation:fab-halo 3.6s ease-out 2.5s infinite;--halo:31,168,85}\n'
    '  .fab-call::after{animation:fab-halo 3.6s ease-out 4.3s infinite;--halo:242,169,59}\n'
    '  .fab-call .icon{animation:lg-ring-idle 7s ease-in-out 6.5s infinite}\n'
    '  .fab-call:hover .icon,.fab-call.tapped .icon{animation:lg-ring .6s var(--ease)}\n'
    '}\n'
    '@keyframes fab-halo{0%{box-shadow:0 0 0 0 rgba(var(--halo),.5)}70%,100%{box-shadow:0 0 0 15px rgba(var(--halo),0)}}\n'
    '.fab-top{width:46px;height:46px;min-height:0;border-radius:50%;margin-right:6px}\n')
rep(".fab-wa,.fab-top,.footer-scene';", ".fab-wa,.fab-call,.fab-top,.footer-scene';")
# (chiffres alignés dans les titres : règle h1-h4 ci-dessus)

# chiffres et prix : Fredoka, comme le logo, bloc balisé avant la fin du style
s = re.sub(r'/\* pb-police:start \*/[\s\S]*?/\* pb-police:end \*/\n?', '', s)
i = s.index('</style>')
s = s[:i] + ('/* pb-police:start */\n'
  '.univ-card .num,.univ-hero .bignum,.pack .big,.stage-age strong,.pro .n,.tstep .num,.notfound .big,.list-total strong{font-family:var(--font-brand)}\n'
    '@media (max-width:620px){.fab-wa,.fab-call{width:52px;height:52px}.fab-wa .icon,.fab-call .icon{width:26px;height:26px}.fabs{gap:9px}}\n'
  '/* pb-police:end */\n') + s[i:]
# « 24 h » ne se coupe plus en fin de ligne
s = s.replace('24 h', '24\u00a0h')

# ---------- 2 bis. pied de page « Restons en contact » (liste avec icônes, comme Keraby) et mention de droits ----------
rep("""        <div class="contact-num"><span class="wa-num"></span><button type="button" class="copy-btn" data-action="copy-num"><svg class="icon"><use href="#i-copy"/></svg><span>Copier</span></button></div>
        <div class="phones" id="phones" style="margin-top:10px" hidden></div>
        <p style="margin-top:8px">Sur WhatsApp, <span class="hours"></span>.</p>""",
"""        <ul class="contact-list">
          <li><svg class="icon"><use href="#i-phone"/></svg><a class="tel-link" href="tel:+2250768211934"><span class="wa-num"></span></a><button type="button" class="copy-btn" data-action="copy-num"><svg class="icon"><use href="#i-copy"/></svg><span>Copier</span></button></li>
          <li><svg class="icon"><use href="#i-wa"/></svg><a class="wa-link" href="#" target="_blank" rel="noopener">WhatsApp</a></li>
          <li id="contact-mail" hidden><svg class="icon"><use href="#i-mail"/></svg><a class="mail-link" href="#"></a></li>
          <li><svg class="icon"><use href="#i-clock"/></svg><span class="hours-cap"></span></li>
        </ul>
        <div class="phones" id="phones" style="margin-top:10px" hidden></div>""")
rep('<div class="footer-bottom"><span>© <span id="year"></span> Petit Baobab. Tous les prix sont en FCFA.</span>',
    '<div class="footer-bottom"><span>© <span id="year"></span> Petit Baobab — Tous droits réservés. Prix en FCFA.</span>')
rep("  hours: 'tous les jours de 8 h à 21 h',", "  hours: 'tous les jours de 8 h à 21 h',\n  email: '',   // adresse e-mail de la boutique : la ligne apparaît dans le pied de page dès qu'elle est remplie")
rep("  $$('.hours').forEach(function(el){ el.textContent = CONFIG.hours; });",
    "  $$('.hours').forEach(function(el){ el.textContent = CONFIG.hours; });\n"
    "  $$('.hours-cap').forEach(function(el){ el.textContent = CONFIG.hours.charAt(0).toUpperCase() + CONFIG.hours.slice(1); });\n"
    "  $$('.tel-link').forEach(function(a){ a.href = 'tel:+' + CONFIG.whatsapp; });\n"
    "  $$('.wa-link').forEach(function(a){ a.href = waLink('Bonjour ' + CONFIG.brand + ', j\\'ai une question.'); });\n"
    "  if (CONFIG.email){ $('#contact-mail').hidden = false; var ml = $('#contact-mail .mail-link'); ml.href = 'mailto:' + CONFIG.email; ml.textContent = CONFIG.email; }")
rep('<symbol id="i-chat" viewBox="0 0 24 24">',
    '<symbol id="i-mail" viewBox="0 0 24 24"><rect x="3" y="5.5" width="18" height="13" rx="2"/><path d="m3.5 7 8.5 6 8.5-6"/></symbol>'
    '<symbol id="i-clock" viewBox="0 0 24 24"><circle cx="12" cy="12" r="8.5"/><path d="M12 7.5V12l3 2"/></symbol>'
    '<symbol id="i-chat" viewBox="0 0 24 24">')
rep('.contact-num{display:flex;align-items:center;gap:8px;flex-wrap:wrap;font-weight:700;font-variant-numeric:tabular-nums}',
    '.contact-num{display:flex;align-items:center;gap:8px;flex-wrap:wrap;font-weight:700;font-variant-numeric:tabular-nums}\n'
    '.contact-list{list-style:none;margin:0;padding:0;display:grid;gap:12px}\n'
    '.contact-list li{display:flex;align-items:center;gap:12px;flex-wrap:wrap;color:var(--footer-ink)}\n'
    '.contact-list li > .icon{width:20px;height:20px;color:var(--accent);flex:none}\n'
    '.contact-list a{color:var(--footer-ink);text-decoration:none;font-weight:700;font-variant-numeric:tabular-nums}\n'
    '.contact-list a:hover{text-decoration:underline;text-underline-offset:3px}\n'
    '.contact-list .copy-btn{margin-left:auto}')

# ---------- 3. ambiance ----------
css = open(os.path.join(HERE, 'ambiance.css'), encoding='utf-8').read().strip()
s = re.sub(r'/\* pb-ambiance:start \*/[\s\S]*?/\* pb-ambiance:end \*/\n?', '', s)
i = s.index('</style>')
s = s[:i] + '/* pb-ambiance:start */\n' + css + '\n/* pb-ambiance:end */\n' + s[i:]
js = open(os.path.join(HERE, 'ambiance.js'), encoding='utf-8').read().strip()
s = re.sub(r'<script id="pb-ambiance">[\s\S]*?</script>\n?', '', s)
assert s.rstrip().endswith('</script>')
s = s.rstrip() + '\n<script id="pb-ambiance">\n' + js + '\n</script>\n'

open(P, 'w', encoding='utf-8').write(s)
print('police, boutons et ambiance en place')
