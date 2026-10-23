"""23 oct. 2026 — commande et fiche article inspirées du parcours EAS :
   - page commande en trois cartes : « Informations de livraison », « Méthode de paiement », « Votre commande » ;
   - second numéro facultatif ; case « J'ai lu et j'accepte les conditions de vente » obligatoire, avec la mention sur les données ;
   - quantités +/− et retrait d'un article directement dans le récapitulatif ;
   - fiche article : encadré « Livraison à domicile » et « Besoin d'aide ? » (WhatsApp, appel).
   Pas de compteur « 17 personnes regardent ce produit » : ce serait un chiffre inventé.
   Idempotent (chaque ajout est protégé par un repère)."""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
P = os.path.join(HERE, '..', 'petit-baobab.html')
s = open(P, encoding='utf-8').read()

def once(marker, old, new, count=1):
    """Remplace `old` par `new` seulement si `marker` n'est pas encore dans la page."""
    global s
    if marker in s: return
    n = s.count(old); assert n == count, (n, old[:90]); s = s.replace(old, new)

# ---------- 1. formulaire : titres de cartes et second numéro ----------
once('id="f-phone2"',
     '      <form class="form" id="form" novalidate>\n        <div class="row2">',
     '      <form class="form" id="form" novalidate>\n        <h3 class="co-title">Informations de livraison</h3>\n        <div class="row2">')
once('id="f-phone2"',
     '<span class="hint">Pour vous appeler avant la livraison.</span><span class="err"></span></div>\n        </div>',
     '<span class="hint">Pour vous appeler avant la livraison.</span><span class="err"></span></div>\n        </div>\n'
     '        <div class="field"><label for="f-phone2">Autre numéro <small class="opt">(facultatif)</small></label><input type="tel" id="f-phone2" autocomplete="tel" placeholder="Un proche joignable si vous ne répondez pas"><span class="err"></span></div>')
once('class="co-title co-pay"',
     '          <span class="legend">Paiement</span>',
     '          <h3 class="co-title co-pay">Méthode de paiement</h3>')
# message WhatsApp : le second numéro
once("L.push('Autre numéro : '",
     "  L.push('Téléphone : ' + (val('f-phone') || '…'));",
     "  L.push('Téléphone : ' + (val('f-phone') || '…'));\n  if (val('f-phone2')) L.push('Autre numéro : ' + val('f-phone2'));")
once("id:'f-phone2'",
     "    {id:'f-zone', ok:function(){ return !!val('f-zone'); }, msg:'Choisissez votre commune.'},",
     "    {id:'f-zone', ok:function(){ return !!val('f-zone'); }, msg:'Choisissez votre commune.'},\n"
     "    {id:'f-phone2', ok:function(){ var d = val('f-phone2').replace(/\\D/g,''); return !d || d.length >= 8; }, msg:'Ce numéro paraît incomplet (au moins 8 chiffres), ou laissez la case vide.'},")

# ---------- 2. récapitulatif : titre, quantités, conditions ----------
once('<h3>Votre commande</h3>\n        <p class="muted" style="font-size:.86rem">Référence',
     '        <h3>Récapitulatif</h3>\n        <p class="muted" style="font-size:.86rem">Référence',
     '        <h3>Votre commande</h3>\n        <p class="muted" style="font-size:.86rem">Référence')
once('id="f-cgv"',
     '        <a class="btn btn-primary btn-block" id="wa-send"',
     '        <p class="co-privacy">Vos coordonnées servent uniquement à préparer et livrer votre commande, comme expliqué dans notre <a href="#confidentialite" class="textlink" data-action="nav" data-view="confidentialite">politique de confidentialité</a>.</p>\n'
     '        <div class="field co-accept"><label class="toggle"><input type="checkbox" id="f-cgv"> <span>J\'ai lu et j\'accepte les <a href="#cgv" class="textlink" data-action="nav" data-view="cgv">conditions de vente</a> <span class="req" aria-hidden="true">*</span></span></label><span class="err" id="cgv-err"></span></div>\n'
     '        <a class="btn btn-primary btn-block" id="wa-send"')
once('data-action="remove" data-id="\' + i.p.id + \'" aria-label="Retirer',
     "  $('#sum-lines').innerHTML = items.map(function(i){ return '<div><span>' + esc(i.p.name) + ' × ' + i.qty + '</span><span class=\"price\">' + fmt(i.p.price*i.qty) + '</span></div>'; }).join('');",
     "  $('#sum-lines').innerHTML = items.map(function(i){ return '<div class=\"co-line\"><button type=\"button\" class=\"co-x\" data-action=\"remove\" data-id=\"' + i.p.id + '\" aria-label=\"Retirer ' + esc(i.p.name) + '\">' + icon('x') + '</button>' +\n"
     "    (i.p.image ? '<img class=\"co-thumb\" src=\"' + esc(img(i.p)) + '\" alt=\"\" loading=\"lazy\">' : '<span class=\"co-thumb\"></span>') +\n"
     "    '<span class=\"co-info\"><span class=\"co-name\">' + esc(i.p.name) + '</span><span class=\"qty qty-sm\"><button type=\"button\" data-action=\"qty-minus\" data-id=\"' + i.p.id + '\" aria-label=\"Moins\">' + icon('minus') + '</button><output>' + i.qty + '</output><button type=\"button\" data-action=\"qty-plus\" data-id=\"' + i.p.id + '\" aria-label=\"Plus\">' + icon('plus') + '</button></span></span>' +\n"
     "    '<span class=\"price\">' + fmt(i.p.price*i.qty) + '</span></div>'; }).join('');")
# la case est obligatoire
once("$('#f-cgv').checked",
     "  var errs = validateFields(orderRules());\n  if (Object.keys(errs).length){ e.preventDefault(); showErrors('#form', '#form-alert', errs); return; }",
     "  var errs = validateFields(orderRules());\n  if (Object.keys(errs).length){ e.preventDefault(); showErrors('#form', '#form-alert', errs); return; }\n"
     "  if (!$('#f-cgv').checked){ e.preventDefault(); var ce = $('#cgv-err'); ce.textContent = 'Cochez la case pour accepter les conditions de vente.'; ce.closest('.field').classList.add('invalid'); try { $('#f-cgv').focus(); } catch(x){} return; }\n"
     "  $('#cgv-err').textContent = ''; $('#cgv-err').closest('.field').classList.remove('invalid');")
once("'#f-cgv').addEventListener",
     "$('#wa-send').addEventListener('click', function(e){ sendOrder(e, this); });",
     "$('#wa-send').addEventListener('click', function(e){ sendOrder(e, this); });\n"
     "$('#f-cgv').addEventListener('change', function(){ if (this.checked){ $('#cgv-err').textContent = ''; $('#cgv-err').closest('.field').classList.remove('invalid'); } });")

# ---------- 3. fiche article : livraison à domicile, besoin d'aide ----------
once('class="help-box"',
     "    '<li>' + icon('check') + '<span>Espèces, Wave ou Mobile Money à la livraison, ou acompte et solde à la réception</span></li></ul>';",
     "    '<li>' + icon('check') + '<span>Espèces, Wave ou Mobile Money à la livraison, ou acompte et solde à la réception</span></li></ul>' +\n"
     "    '<div class=\"help-box\"><div class=\"hb-row\"><span class=\"hb-ico\">' + icon('truck') + '</span><div><strong>Livraison à domicile</strong><p>On vous livre chez vous, en moins de 24 h à Abidjan. Ajoutez l\\'article au panier, puis envoyez la commande sur WhatsApp : on vous rappelle pour confirmer.</p></div></div>' +\n"
     "    '<div class=\"hb-row\"><span class=\"hb-ico hb-wa\">' + icon('wa') + '</span><div><strong>Besoin d\\'aide ?</strong><p>Un doute sur le modèle, la couleur ou la taille ? <a class=\"textlink\" href=\"' + esc(waLink('Bonjour ' + CONFIG.brand + ', j\\'ai une question sur cet article.')) + '\" target=\"_blank\" rel=\"noopener\">Écrivez-nous sur WhatsApp</a> ou appelez le <a class=\"textlink\" href=\"tel:+' + CONFIG.whatsapp + '\">' + esc(CONFIG.whatsappDisplay) + '</a>.</p></div></div></div>';")

# la fiche passe l'article au bloc : le lien WhatsApp cite son nom et sa référence ; l'ancienne ligne « Une question sur cet article ? » fait doublon
once('function reassure(p){', 'function reassure(){', 'function reassure(p){')
once("    reassure(p) +", "    reassure() +", "    reassure(p) +")
s = s.replace("esc(waLink('Bonjour ' + CONFIG.brand + ', j\\'ai une question sur cet article.'))",
              "esc(waLink(p ? 'Bonjour, une question sur « ' + p.name + ' »' + (p.ref ? ' (réf. ' + p.ref + ')' : '') + '.' : 'Bonjour ' + CONFIG.brand + ', j\\'ai une question.'))")
OLDQ = "    '<p class=\"wa-note\" style=\"margin-top:12px\">Une question sur cet article ? <a class=\"textlink\" href=\"' + waLink('Bonjour, une question sur « ' + p.name + ' »' + (p.ref ? ' (réf. ' + p.ref + ')' : '') + '.') + '\" target=\"_blank\" rel=\"noopener\">Demandez-nous sur WhatsApp</a>.</p>' +\n"
if OLDQ in s: s = s.replace(OLDQ, '')

# ---------- 3 bis. champs obligatoires marqués d'un astérisque et vérifiés (nom, numéro, commune, quartier) ----------
R = ' <span class="req" aria-hidden="true">*</span>'
once('Votre nom' + R, '<label for="f-name">Votre nom</label><input type="text" id="f-name" autocomplete="name" placeholder="Prénom et nom" required>',
     '<label for="f-name">Votre nom' + R + '</label><input type="text" id="f-name" autocomplete="name" placeholder="Prénom et nom" required aria-required="true" maxlength="80">')
once('Votre numéro' + R, '<label for="f-phone">Votre numéro</label><input type="tel" id="f-phone" autocomplete="tel" placeholder="07 00 00 00 00" required>',
     '<label for="f-phone">Votre numéro' + R + '</label><input type="tel" id="f-phone" autocomplete="tel" inputmode="tel" placeholder="07 00 00 00 00" required aria-required="true" maxlength="20">')
once('Commune de livraison' + R, '<label for="f-zone">Commune de livraison</label><select id="f-zone" required>',
     '<label for="f-zone">Commune de livraison' + R + '</label><select id="f-zone" required aria-required="true">')
once('Quartier et repère' + R, '<label for="f-address">Quartier et repère</label><input type="text" id="f-address" placeholder="Ex. : Riviera 3, près de la pharmacie…"></div>',
     '<label for="f-address">Quartier et repère' + R + '</label><input type="text" id="f-address" placeholder="Ex. : Riviera 3, près de la pharmacie…" required aria-required="true" maxlength="160"><span class="err"></span></div>')
once('Nom de la maman' + R, '<label for="g-name">Nom de la maman</label>', '<label for="g-name">Nom de la maman' + R + '</label>')
once('Son numéro <small class="opt">', '<label for="g-phone">Son numéro</label>', '<label for="g-phone">Son numéro <small class="opt">(facultatif)</small></label>')
once('Votre message pour la carte <small class="opt">', '<label for="g-msg">Votre message pour la carte</label>', '<label for="g-msg">Votre message pour la carte <small class="opt">(facultatif)</small></label>')
once('heure souhaitée) <small class="opt">', '<label for="f-note">Précisions (couleurs, modèles, heure souhaitée)</label>', '<label for="f-note">Précisions (couleurs, modèles, heure souhaitée) <small class="opt">(facultatif)</small></label>')
once('class="req-note"', '        <h3 class="co-title">Informations de livraison</h3>',
     '        <h3 class="co-title">Informations de livraison</h3>\n        <p class="req-note">Les champs marqués d\'un <span class="req">*</span> sont obligatoires.</p>')
# règles plus strictes : numéro ivoirien (10 chiffres, avec ou sans +225), nom de 2 lettres au moins, quartier renseigné
once('function ciPhone(', 'function orderRules(){',
     "function ciPhone(v){ var d = String(v || '').replace(/\\D/g, ''); if (d.indexOf('00225') === 0) d = d.slice(5); else if (d.indexOf('225') === 0 && d.length === 13) d = d.slice(3); return d.length === 10 || (d.length >= 8 && d.length <= 15 && /^\\+|^00/.test(String(v).trim())); }\n"
     "function orderRules(){")
once("msg:'Indiquez un numéro ivoirien à 10 chiffres",
     "    {id:'f-name', ok:function(){ return !!val('f-name'); }, msg:'Indiquez votre nom.'},\n    {id:'f-phone', ok:function(){ return val('f-phone').replace(/\\D/g,'').length >= 8; }, msg:'Indiquez un numéro valide (au moins 8 chiffres).'},",
     "    {id:'f-name', ok:function(){ return val('f-name').replace(/[^A-Za-zÀ-ÿ]/g,'').length >= 2; }, msg:'Indiquez votre nom (au moins 2 lettres).'},\n"
     "    {id:'f-phone', ok:function(){ return ciPhone(val('f-phone')); }, msg:'Indiquez un numéro ivoirien à 10 chiffres (ex. 07 00 00 00 00), ou un numéro étranger commençant par +.'},\n"
     "    {id:'f-address', ok:function(){ return val('f-address').length >= 3; }, msg:'Indiquez votre quartier et un repère pour le livreur.'},")
once("ciPhone(val('f-phone2'))",
     "    {id:'f-phone2', ok:function(){ var d = val('f-phone2').replace(/\\D/g,''); return !d || d.length >= 8; }, msg:'Ce numéro paraît incomplet (au moins 8 chiffres), ou laissez la case vide.'},",
     "    {id:'f-phone2', ok:function(){ return !val('f-phone2') || ciPhone(val('f-phone2')); }, msg:'Ce numéro paraît incomplet (10 chiffres), ou laissez la case vide.'},")
once('.req-note{', '/* Commande et fiche article (brand/commande.py) */',
     '/* Commande et fiche article (brand/commande.py) */\n.req{color:var(--danger);font-weight:700}\n.req-note{font-size:.86rem;color:var(--muted);margin:0 0 4px}')

# ---------- 4. styles ----------
CSS = '''/* Commande et fiche article (brand/commande.py) */
.co-title{font-size:1.25rem;margin:0 0 4px}
.co-pay{margin-top:6px}
.opt{font-weight:400;color:var(--muted);font-size:.82em}
.co-privacy{font-size:.86rem;color:var(--muted);margin:14px 0 8px}
.co-accept{margin:0 0 12px}
.co-accept .toggle{align-items:flex-start;gap:10px;font-weight:600}
.co-accept input{margin-top:3px;width:18px;height:18px;accent-color:var(--brand);flex:none}
.co-accept .req{color:var(--danger)}
.co-accept.invalid .toggle{color:var(--danger)}
#sum-lines .co-line{display:grid;grid-template-columns:auto 52px 1fr auto;align-items:center;gap:10px;padding:10px 0;border-bottom:1px solid var(--line)}
#sum-lines .co-line:last-child{border-bottom:0}
.co-x{width:28px;height:28px;border-radius:50%;border:0;background:transparent;color:var(--muted);display:grid;place-items:center;padding:0}
.co-x:hover{background:var(--surface-2);color:var(--danger)}
.co-x .icon{width:16px;height:16px}
.co-thumb{width:52px;height:52px;border-radius:10px;object-fit:cover;background:var(--surface-2);display:block}
.co-info{display:grid;gap:6px;min-width:0}
.co-name{font-weight:600;font-size:.92rem;line-height:1.3}
.qty-sm{justify-self:start;transform-origin:left center;transform:scale(.86)}
.help-box{margin-top:14px;border:1px solid var(--line);border-radius:var(--radius);padding:14px 16px;display:grid;gap:14px;background:var(--surface)}
.hb-row{display:grid;grid-template-columns:auto 1fr;gap:12px;align-items:start}
.hb-row strong{display:block;margin-bottom:2px}
.hb-row p{margin:0;color:var(--muted);font-size:.92rem}
.hb-ico{width:38px;height:38px;border-radius:50%;display:grid;place-items:center;background:var(--accent-soft);color:var(--accent)}
.hb-ico .icon{width:20px;height:20px}
.hb-ico.hb-wa{background:var(--ok-soft);color:var(--wa)}
'''
if '/* Commande et fiche article (brand/commande.py) */' not in s:
    i = s.index('</style>'); s = s[:i] + CSS + s[i:]

open(P, 'w', encoding='utf-8').write(s)
print('commande et fiche article en place')
