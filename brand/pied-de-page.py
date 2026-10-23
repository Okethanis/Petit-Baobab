"""23 oct. 2026 — pied de page rangé comme les boutiques d'ici (inspiration EAS) :
   colonnes « Boutique » et « À propos », et deux nouvelles pages : « Contactez-nous » et « Retours et échanges ».
   Les textes ne reprennent que ce que le site dit déjà (échange sous 48 h, vérification à la livraison, annulation sous 24 h).
   Idempotent."""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
P = os.path.join(HERE, '..', 'petit-baobab.html')
s = open(P, encoding='utf-8').read()

def rep(old, new, count=1):
    global s
    if new in s: return                                # déjà fait (y compris quand « new » commence par « old »)
    n = s.count(old)
    assert n == count, (n, old[:90]); s = s.replace(old, new)

# ---------- 1. les deux pages ----------
PAGES = '''<section class="view" id="v-contact" hidden>
  <div class="wrap section">
    <nav class="crumbs" aria-label="Fil d'Ariane" data-crumbs></nav>
    <h2 class="view-title">Contactez-nous</h2>
    <p class="lead muted" style="max-width:60ch">Une question sur un article, une taille, une livraison ? On vous répond <span class="hours"></span>.</p>
    <div class="contact-cards">
      <a class="contact-card tel-link" href="tel:+2250152358122"><span class="cc-ico"><svg class="icon"><use href="#i-phone"/></svg></span><span><strong>Appeler</strong><span class="wa-num">+225 01 52 35 81 22</span></span></a>
      <a class="contact-card wa-link" href="#" target="_blank" rel="noopener"><span class="cc-ico cc-wa"><svg class="icon"><use href="#i-wa"/></svg></span><span><strong>WhatsApp</strong><span>Écrire maintenant</span></span></a>
      <a class="contact-card mail-link-card" href="#" id="contact-mail-card" hidden><span class="cc-ico"><svg class="icon"><use href="#i-mail"/></svg></span><span><strong>E-mail</strong><span class="mail-text"></span></span></a>
      <div class="contact-card"><span class="cc-ico"><svg class="icon"><use href="#i-clock"/></svg></span><span><strong>Horaires</strong><span class="hours-cap"></span></span></div>
    </div>
    <form class="panel contact-form" id="contact-form" novalidate>
      <h3>Nous écrire</h3>
      <p class="muted">Votre message s'ouvre dans WhatsApp, prêt à envoyer.</p>
      <label>Votre prénom<input type="text" id="cf-name" autocomplete="given-name" required></label>
      <label>Votre message<textarea id="cf-msg" rows="4" required placeholder="Par exemple : la poussette G606 existe-t-elle en gris ?"></textarea></label>
      <p class="form-err" id="cf-err" hidden>Écrivez votre prénom et votre message.</p>
      <button type="submit" class="btn btn-primary"><svg class="icon"><use href="#i-wa"/></svg><span>Envoyer sur WhatsApp</span></button>
    </form>
  </div>
</section>

<section class="view" id="v-retours" hidden>
  <div class="wrap section prose">
    <nav class="crumbs" aria-label="Fil d'Ariane" data-crumbs></nav>
    <h2 class="view-title">Retours et échanges</h2>
    <p class="updated">Dernière mise à jour : <span class="legal-date"></span></p>
    <h3>Vous vérifiez avant de payer</h3><p>À la livraison, l'article est déballé devant vous. Prenez le temps de le regarder avant de le régler.</p>
    <h3>Échange sous 48 h</h3><p>Un article abîmé ou qui ne correspond pas à votre commande est échangé sous 48 h après réception, dans son emballage d'origine, sur présentation d'une photo.</p>
    <h3>Comment faire</h3><ol><li>Écrivez-nous sur WhatsApp au <span class="wa-num"></span> avec la référence de votre commande (elle commence par PB-).</li><li>Joignez une photo de l'article et de son emballage.</li><li>On vous répond pour organiser l'échange.</li></ol>
    <h3>Modifier ou annuler une commande</h3><p>C'est possible dans les 24 heures qui suivent la commande, sur WhatsApp, avec sa référence. Le détail est dans les <a href="#cgv" class="textlink" data-action="nav" data-view="cgv">Conditions de vente</a>.</p>
    <div class="cta-row"><a class="btn btn-primary wa-link" href="#" target="_blank" rel="noopener"><svg class="icon"><use href="#i-wa"/></svg><span>Demander un échange sur WhatsApp</span></a><a href="#contact" class="btn btn-ghost" data-action="nav" data-view="contact">Contactez-nous</a></div>
  </div>
</section>

'''
if 'id="v-contact"' not in s: rep('<section class="view" id="v-cgu" hidden>', PAGES + '<section class="view" id="v-cgu" hidden>')
if "  contact:         {" not in s: rep("  cgu:             { path: '/conditions-d-utilisation/',",
    "  contact:         { path: '/contactez-nous/', nav: 'Contactez-nous', title: 'Contactez-nous · Petit Baobab', description: 'Téléphone, WhatsApp, e-mail et horaires de Petit Baobab. Une question sur un article ou une livraison ? On vous répond.' },\n"
    "  retours:         { path: '/retours-et-echanges/', nav: 'Retours et échanges', title: 'Retours et échanges · Petit Baobab', description: 'Vérification à la livraison, échange sous 48 h d\\'un article abîmé ou non conforme, annulation sous 24 h.' },\n"
    "  cgu:             { path: '/conditions-d-utilisation/',")
if "{ view:'contact'" not in s: rep("  { view:'livraison', kw:",
    "  { view:'contact', kw:'contact contacter appeler téléphone numéro whatsapp email e-mail mail horaires joindre' },\n"
    "  { view:'retours', kw:'retour retours échange échanger remboursement défaut abîmé annuler annulation garantie' },\n"
    "  { view:'livraison', kw:")

# ---------- 2. le formulaire « Nous écrire » et l'e-mail sur la page contact ----------
if "#contact-mail-card'); if" not in s: rep("  if (CONFIG.email){ $('#contact-mail').hidden = false;",
    "  if (CONFIG.email){ var mc = $('#contact-mail-card'); if (mc){ mc.hidden = false; mc.href = 'mailto:' + CONFIG.email; mc.querySelector('.mail-text').textContent = CONFIG.email; } }\n"
    "  var cf = $('#contact-form'); if (cf) cf.addEventListener('submit', function(e){ e.preventDefault(); var n = $('#cf-name').value.trim(), m = $('#cf-msg').value.trim(); $('#cf-err').hidden = !!(n && m); if (!n || !m) return; window.open(waLink('Bonjour ' + CONFIG.brand + ', c\\'est ' + n + '. ' + m), '_blank', 'noopener'); });\n"
    "  if (CONFIG.email){ $('#contact-mail').hidden = false;")

# ---------- 3. le pied de page en colonnes ----------
OLD_LINKS = '''      <div>
        <h4>Informations</h4>
        <ul id="footer-links">
          <li><a href="#packs" data-action="nav" data-view="packs">Packs naissance</a></li>
          <li><a href="#valise" data-action="nav" data-view="valise">Valise de maternité</a></li>
          <li><a href="#guide" data-action="nav" data-view="guide">Que prévoir mois par mois</a></li>
          <li><a href="#conseils" data-action="nav" data-view="conseils">Conseils d'achat</a></li>
          <li><a href="#liste" data-action="nav" data-view="liste">Liste de naissance</a></li>
          <li><a href="#histoire" data-action="nav" data-view="histoire">Notre histoire</a></li>
          <li><a href="#livraison" data-action="nav" data-view="livraison">Livraison, paiement et questions fréquentes</a></li>
          <li><a href="#cgv" data-action="nav" data-view="cgv">Conditions de vente</a></li>
          <li><a href="#cgu" data-action="nav" data-view="cgu">Conditions d'utilisation</a></li>
          <li><a href="#confidentialite" data-action="nav" data-view="confidentialite">Confidentialité</a></li>
          <li><a href="#compte" data-action="account">Mon compte</a></li>
          <li id="cookie-link" hidden><button type="button" class="flink" data-action="consent-open">Gérer les cookies</button></li>
        </ul>
      </div>'''
NEW_LINKS = '''      <div>
        <h4>Boutique</h4>
        <ul class="footer-links">
          <li><a href="#packs" data-action="nav" data-view="packs">Packs naissance</a></li>
          <li><a href="#valise" data-action="nav" data-view="valise">Valise de maternité</a></li>
          <li><a href="#liste" data-action="nav" data-view="liste">Liste de naissance</a></li>
          <li><a href="#cadeaux" data-action="nav" data-view="cadeaux">Cadeaux de naissance</a></li>
          <li><a href="#guide" data-action="nav" data-view="guide">Que prévoir mois par mois</a></li>
          <li><a href="#conseils" data-action="nav" data-view="conseils">Conseils d'achat</a></li>
          <li><a href="#histoire" data-action="nav" data-view="histoire">Notre histoire</a></li>
        </ul>
      </div>
      <div>
        <h4>À propos</h4>
        <ul class="footer-links" id="footer-links">
          <li><a href="#contact" data-action="nav" data-view="contact">Contactez-nous</a></li>
          <li><a href="#livraison" data-action="nav" data-view="livraison">Livraison, paiement et FAQ</a></li>
          <li><a href="#retours" data-action="nav" data-view="retours">Retours et échanges</a></li>
          <li><a href="#cgv" data-action="nav" data-view="cgv">Conditions de vente</a></li>
          <li><a href="#cgu" data-action="nav" data-view="cgu">Conditions d'utilisation</a></li>
          <li><a href="#confidentialite" data-action="nav" data-view="confidentialite">Politique de confidentialité</a></li>
          <li><a href="#compte" data-action="account">Mon compte</a></li>
          <li id="cookie-link" hidden><button type="button" class="flink" data-action="consent-open">Gérer les cookies</button></li>
        </ul>
      </div>'''
rep(OLD_LINKS, NEW_LINKS)
rep('@media(min-width:760px){.footer-grid{grid-template-columns:1.4fr 1fr 1fr}}',
    '@media(min-width:620px){.footer-grid{grid-template-columns:1fr 1fr}}\n@media(min-width:1000px){.footer-grid{grid-template-columns:1.35fr 1.1fr .9fr .9fr}}')

# ---------- 4. styles des nouvelles pages ----------
CSS = '''/* Contactez-nous */
.contact-cards{display:grid;gap:12px;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));margin:var(--sp-4) 0}
.contact-card{display:flex;align-items:center;gap:14px;background:var(--surface);border:1px solid var(--line);border-radius:var(--radius);padding:16px;text-decoration:none;color:var(--ink);transition:transform .2s var(--ease),box-shadow .2s var(--ease)}
a.contact-card:hover{transform:translateY(-2px);box-shadow:var(--shadow)}
.contact-card strong{display:block;font-size:1.02rem}
.contact-card strong + span{color:var(--muted);font-variant-numeric:tabular-nums;word-break:break-word}
.cc-ico{width:46px;height:46px;border-radius:50%;display:grid;place-items:center;background:var(--accent-soft);color:var(--accent);flex:none}
.cc-ico .icon{width:22px;height:22px}
.cc-ico.cc-wa{background:var(--ok-soft);color:var(--wa)}
.contact-form{display:grid;gap:12px;max-width:560px}
.contact-form label{display:grid;gap:6px;font-weight:600}
.contact-form .btn{justify-self:start}
.form-err{color:var(--danger);font-weight:600;margin:0}
.prose ol{padding-left:1.3em;display:grid;gap:6px}
'''
if '/* Contactez-nous */' not in s:
    i = s.index('</style>'); s = s[:i] + CSS + s[i:]

open(P, 'w', encoding='utf-8').write(s)
print('pied de page et pages contact / retours en place')
