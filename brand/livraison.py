"""23 oct. 2026 — commune de livraison choisie une fois, prix de livraison partout :
   - sélecteur de commune groupé (Abidjan, Grand Abidjan, Hors Abidjan) sur la page commande, dans le panier et sur la fiche article ;
   - la commune est retenue (navigateur du visiteur) et synchronisée entre les trois endroits ;
   - le panier affiche frais, total et ce qu'il manque pour la livraison offerte ;
   - « Quartier et repère » propose les quartiers connus de la commune choisie (saisie libre possible).
   Les frais viennent de CONFIG.zones, qui reste la seule source des prix. Idempotent."""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
P = os.path.join(HERE, '..', 'petit-baobab.html')
s = open(P, encoding='utf-8').read()

def once(marker, old, new, count=1):
    global s
    if marker in s: return
    n = s.count(old); assert n == count, (n, old[:90]); s = s.replace(old, new)

# ---------- 1. groupes de communes et quartiers ----------
once('  zoneGroups:',
     "    ['Hors Abidjan (envoi par car)', null]\n  ],",
     "    ['Hors Abidjan (envoi par car)', null]\n  ],\n"
     "  zoneGroups: [['Abidjan', ['Abobo', 'Adjamé', 'Attécoubé', 'Cocody', 'Koumassi', 'Marcory', 'Plateau', 'Port-Bouët', 'Treichville', 'Yopougon']], ['Grand Abidjan', ['Bingerville', 'Anyama', 'Songon']], ['Ailleurs en Côte d\\'Ivoire', ['Hors Abidjan (envoi par car)']]],\n"
     "  quartiers: {   // suggestions pour « Quartier et repère » (le client peut écrire autre chose)\n"
     "    'Abobo': ['Abobo Gare', 'PK 18', 'Avocatier', 'Abobo Baoulé', 'Belleville', 'N\\'Dotré', 'Anonkoua-Kouté', 'Sagbé', 'Akeikoi', 'Abobo Té'],\n"
     "    'Adjamé': ['Adjamé Liberté', 'Williamsville', '220 Logements', 'Bracodi', 'Mairie', 'Paillet', 'Dallas', 'Renault'],\n"
     "    'Attécoubé': ['Santé', 'Locodjro', 'Agban', 'Abobo-Doumé', 'Mossikro', 'Sebroko'],\n"
     "    'Cocody': ['Riviera 2', 'Riviera 3', 'Riviera Palmeraie', 'Riviera Golf', 'Angré', 'Deux-Plateaux', 'Vallon', 'Blockhaus', 'Danga', 'Ambassades', 'Saint-Jean', 'Faya', 'M\\'Pouto', 'Akouédo', 'Bonoumin', 'Cité des Arts', 'Mermoz'],\n"
     "    'Koumassi': ['Remblais', 'Sicogi', 'Grand Campement', 'Koumassi Centre', 'Prodomo', 'Soweto', 'Divo'],\n"
     "    'Marcory': ['Zone 4', 'Biétry', 'Marcory Résidentiel', 'Anoumabo', 'Hibiscus', 'Champroux', 'Sans-Fil', 'Konan Raphaël'],\n"
     "    'Plateau': ['Plateau Centre', 'Indénié', 'Cité Administrative'],\n"
     "    'Port-Bouët': ['Vridi', 'Gonzagueville', 'Aéroport', 'Adjahui', 'Jean Folly', 'Derrière Wharf', 'Anani'],\n"
     "    'Treichville': ['Arras', 'Biafra', 'Zone 1', 'Zone 2', 'France-Amérique', 'Gare Lagunaire'],\n"
     "    'Yopougon': ['Niangon', 'Selmer', 'Maroc', 'Toits Rouges', 'Sicogi', 'Andokoi', 'Wassakara', 'Port-Bouët 2', 'Ananeraie', 'Gesco', 'Siporex', 'Kouté', 'Sideci', 'Banco'],\n"
     "    'Bingerville': ['Bingerville Centre', 'Akandjé', 'Gbagba', 'Fêtê', 'Abatta'],\n"
     "    'Anyama': ['Anyama Centre', 'Ahoué', 'Ebimpé', 'Akoupé-Zeudji'],\n"
     "    'Songon': ['Songon Agban', 'Songon Kassemblé', 'Songon M\\'Bratté', 'Songon Té'],\n"
     "    'Hors Abidjan (envoi par car)': ['Bouaké', 'Yamoussoukro', 'San-Pédro', 'Daloa', 'Korhogo', 'Grand-Bassam', 'Abengourou', 'Man', 'Gagnoa', 'Divo']\n"
     "  },")

# ---------- 2. page commande : options groupées, quartiers proposés ----------
once('function zoneOptions(',
     "  CONFIG.zones.forEach(function(z){ var o = document.createElement('option'); o.value = z[0]; o.textContent = z[0] + (z[1]===null ? '' : ' · ' + fmt(z[1])); sel.appendChild(o); });",
     "  sel.innerHTML = zoneOptions('Choisir votre commune…');\n"
     "  var dl = document.createElement('datalist'); dl.id = 'quartiers'; document.body.appendChild(dl); $('#f-address').setAttribute('list', 'quartiers'); $('#f-address').setAttribute('autocomplete', 'off');\n"
     "  if (store('pb-zone')) setZone(store('pb-zone'), true);")
once('function setZone(',
     "function zoneFee(zoneName, sub){",
     "/* Commune de livraison : un seul choix, retenu et repris partout (commande, panier, fiche article) */\n"
     "function zoneOptions(placeholder){\n"
     "  var fees = {}; CONFIG.zones.forEach(function(z){ fees[z[0]] = z[1]; });\n"
     "  return '<option value=\"\">' + esc(placeholder) + '</option>' + (CONFIG.zoneGroups || [['', CONFIG.zones.map(function(z){ return z[0]; })]]).map(function(g){\n"
     "    return '<optgroup label=\"' + esc(g[0]) + '\">' + g[1].filter(function(n){ return n in fees; }).map(function(n){ return '<option value=\"' + esc(n) + '\">' + esc(n) + (fees[n]===null ? ' · frais selon la ville' : ' · ' + fmt(fees[n])) + '</option>'; }).join('') + '</optgroup>';\n"
     "  }).join('');\n"
     "}\n"
     "function currentZone(){ return (state && state.zone) || ''; }\n"
     "function setZone(z, silent){\n"
     "  var ok = CONFIG.zones.some(function(x){ return x[0] === z; }); if (!ok) z = '';\n"
     "  state.zone = z; store('pb-zone', z || null);\n"
     "  var f = $('#f-zone'); if (f && f.value !== z) f.value = z;\n"
     "  $$('.zone-pick').forEach(function(s){ if (s.value !== z) s.value = z; });\n"
     "  var dl = $('#quartiers'); if (dl) dl.innerHTML = ((CONFIG.quartiers || {})[z] || []).map(function(q){ return '<option value=\"' + esc(q) + '\">'; }).join('');\n"
     "  $$('.dl-line').forEach(function(el){ el.innerHTML = deliveryLine(+el.getAttribute('data-price') || 0); });\n"
     "  if (!silent){ try { updateCheckout(); } catch(e){} try { renderCart(); } catch(e){} }\n"
     "}\n"
     "function deliveryLine(extra){\n"
     "  var z = currentZone(), sub = subtotal() + (extra || 0), f = zoneFee(z, sub);\n"
     "  if (!z) return 'Choisissez votre commune pour voir le prix de la livraison.';\n"
     "  if (!f.known) return 'Hors Abidjan : envoi par car, frais selon la ville (on vous les donne sur WhatsApp).';\n"
     "  if (f.fee === 0) return '<strong>Livraison offerte</strong> à ' + esc(z) + ', en moins de 24 h.';\n"
     "  var left = CONFIG.freeDeliveryFrom - sub;\n"
     "  return 'Livraison à ' + esc(z) + ' : <strong>' + fmt(f.fee) + '</strong>, en moins de 24 h. ' + (left > 0 ? 'Offerte dès ' + fmt(CONFIG.freeDeliveryFrom) + ' d\\'achat.' : '');\n"
     "}\n"
     "function zoneFee(zoneName, sub){")
once("classList.contains('zone-pick'))) setZone(e.target.value)",
     "$('#form').addEventListener('input', updateCheckout);",
     "document.addEventListener('change', function(e){ if (e.target && (e.target.id === 'f-zone' || e.target.classList.contains('zone-pick'))) setZone(e.target.value); });\n"
     "$('#form').addEventListener('input', updateCheckout);")

# ---------- 3. panier : commune, frais, total, reste pour la livraison offerte ----------
once("class=\"zone-pick\" aria-label=\"Commune de livraison\"' + (",
     "  $('#drawer-foot').innerHTML = '<div class=\"totals\"><div><span>Sous-total</span><span class=\"price\" id=\"drawer-sub\"></span></div><div class=\"muted\"><span>Livraison</span><span>' + (sub>=CONFIG.freeDeliveryFrom ? 'offerte à Abidjan' : 'selon la commune, dès ' + fmt(minFee)) + '</span></div></div>' +",
     "  var zn = currentZone(), zf = zoneFee(zn, sub), left = CONFIG.freeDeliveryFrom - sub, pct = Math.max(0, Math.min(100, Math.round(sub / CONFIG.freeDeliveryFrom * 100)));\n"
     "  $('#drawer-foot').innerHTML = '<label class=\"zone-row\"><span>Livrer à</span><select class=\"zone-pick\" aria-label=\"Commune de livraison\"' + (zn ? '' : ' data-empty=\"1\"') + '>' + zoneOptions('Choisir la commune…') + '</select></label>' +\n"
     "    '<div class=\"free-bar\" role=\"img\" aria-label=\"' + (left > 0 ? 'Plus que ' + fmt(left) + ' pour la livraison offerte' : 'Livraison offerte') + '\"><i style=\"width:' + pct + '%\"></i></div>' +\n"
     "    '<p class=\"free-note\">' + (left > 0 ? 'Plus que <strong>' + fmt(left) + '</strong> pour la livraison offerte à Abidjan.' : '<strong>Livraison offerte</strong> à Abidjan.') + '</p>' +\n"
     "    '<div class=\"totals\"><div><span>Sous-total</span><span class=\"price\" id=\"drawer-sub\"></span></div>' +\n"
     "    '<div class=\"muted\"><span>Livraison</span><span>' + (zn ? esc(zf.label) : (sub>=CONFIG.freeDeliveryFrom ? 'offerte à Abidjan' : 'dès ' + fmt(minFee))) + '</span></div>' +\n"
     "    (zn && zf.known ? '<div class=\"grand\"><span>Total</span><span class=\"price\">' + fmt(sub + zf.fee) + '</span></div>' : '') + '</div>' +")
once("$$('#drawer-foot .zone-pick')",
     "  tickTo('drawer-sub', $('#drawer-sub'), sub);\n}",
     "  tickTo('drawer-sub', $('#drawer-sub'), sub);\n  $$('#drawer-foot .zone-pick').forEach(function(s){ s.value = zn; });\n}")

# ---------- 4. fiche article : ligne de livraison ----------
once('class="dl-box"',
     "    reassure(p) +",
     "    '<div class=\"dl-box\"><label class=\"zone-row\"><span>' + icon('truck') + 'Livrer à</span><select class=\"zone-pick\" aria-label=\"Commune de livraison\">' + zoneOptions('Choisir la commune…') + '</select></label><p class=\"dl-line\" data-price=\"' + (p.price || 0) + '\">' + deliveryLine(p.price || 0) + '</p></div>' +\n"
     "    reassure(p) +")
once("$$('#sheet .zone-pick')",
     "function openProduct(id){",
     "function syncSheetZone(){ $$('#sheet .zone-pick').forEach(function(s){ s.value = currentZone(); }); }\n"
     "function openProduct(id){")
once("syncSheetZone();",
     "function openSheet(html){ $('#sheet-body').innerHTML = html;",
     "function openSheet(html){ $('#sheet-body').innerHTML = html; syncSheetZone();")

# ---------- 5. styles ----------
CSS = '''/* Commune de livraison (brand/livraison.py) */
.zone-row{display:flex;align-items:center;gap:10px;font-weight:600;font-size:.92rem}
.zone-row > span{display:inline-flex;align-items:center;gap:6px;white-space:nowrap}
.zone-row .icon{width:18px;height:18px;color:var(--accent)}
.zone-pick{flex:1;min-width:0;height:40px;padding:0 10px;border:1px solid var(--line);border-radius:10px;background:var(--surface);color:var(--ink);font:inherit;font-weight:600}
.zone-pick[data-empty]{border-color:var(--accent)}
.drawer-foot .zone-row{margin-bottom:10px}
.free-bar{height:6px;border-radius:99px;background:var(--surface-2);overflow:hidden}
.free-bar i{display:block;height:100%;background:linear-gradient(90deg,var(--accent),var(--brand));border-radius:inherit;transition:width .5s var(--ease)}
.free-note{font-size:.84rem;color:var(--muted);margin:6px 0 10px}
.dl-box{margin-top:14px;padding:12px 14px;border-radius:var(--radius);background:var(--brand-soft);display:grid;gap:8px}
.dl-line{margin:0;font-size:.9rem;color:var(--ink)}
'''
if '/* Commune de livraison (brand/livraison.py) */' not in s:
    i = s.index('</style>'); s = s[:i] + CSS + s[i:]

open(P, 'w', encoding='utf-8').write(s)
print('commune de livraison en place')
