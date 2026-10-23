"""Codes d'articles (id) sans les quantités de packing list (demande de Hanis, 23 oct. 2026).
   Ex. « bjj-601-grey-20-khaki-20 » devient « bjj-601 ».
   - petit-baobab.html : l'id dans PRODUCTS (et partout où il est cité entre apostrophes), le nom de la photo.
   - Ancien code → nouveau dans ID_ALIAS : les paniers, listes de naissance (liens ?l=) et favoris déjà
     enregistrés chez les clients sont convertis au chargement, rien n'est perdu.
   - Renomme images/<ancien>.webp, la clé dans photos/sources.json et admin/thumbs.json.
   Relançable sans rien dupliquer."""
import json, os, re, subprocess

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
HTML = os.path.join(ROOT, 'petit-baobab.html')

# ancien → nouveau (les plus longs d'abord : « ybl-1518-50-2 » avant « ybl-1518-50 »)
IDS = [
    ('ybl-1518-50-2', 'ybl-1518-2'),
    ('ybl-1518-50', 'ybl-1518'),
    ('qs11-2-1', 'qs11'),
    ('kdd17-2-1', 'kdd17'),
    ('kdd18-2-1', 'kdd18'),
    ('3350-2-1', '3350'),
    ('tm716-2-1', 'tm716-b'),
    ('bjj-601-grey-20-khaki-20', 'bjj-601'),
    ('620-2-1', '620'),
    ('bp-301-grey-20-red-10', 'bp-301'),
    ('g600-grey-1-coffee-1', 'g600'),
    ('b05d-grey-5-khaki-5', 'b05d'),
    ('5800-60-40-20', '5800-b'),
    ('109-4-8619-30-60-60', '109-4-8619'),
    ('1688-30-50-20', 'set-bain-grenouille'),
    ('9-80-20-50', 'set-bain-9'),
    ('103-100-60-40', '103'),
    ('hh727-50-50-30-30-30-30', 'hh727'),
    ('hh727-60-40-40-40-20-20', 'hh727-b'),
    ('hh739-10-200-120-80', 'hh739-10'),
    ('5100-180-100-180-100', '5100'),
    ('70-140cm-1pcs-50-90cm-2pcs-n', 'serviettes-70x140'),
    ('b1688-4-4-4-4', 'b1688'),
    ('677137-4-5', '677137'),
    ('7532-5-5', '7532-b'),
    ('hh7031-2-2', 'hh7031'),
    ('38513-1-3-15-15', '38513'),
    ('ty01-each-color-5', 'ty01'),
]

s = open(HTML, encoding='utf-8').read()
start = s.index('var PRODUCTS')
ids_now = set(re.findall(r"\{id:'([^']+)'", s[start:s.index('];', start)]))
done = []
for old, new in IDS:
    if old not in ids_now:
        continue
    assert new not in ids_now, 'nouveau code déjà pris : ' + new
    s = s.replace("'" + old + "'", "'" + new + "'")
    s = s.replace('images/' + old + '.webp', 'images/' + new + '.webp')
    ids_now.discard(old); ids_now.add(new); done.append((old, new))

# conversion des anciens codes chez les clients (panier, liste, favoris) : brand/alias.json, partagé avec brand/doublons.py
AP = os.path.join(ROOT, 'brand', 'alias.json')
AL = json.load(open(AP, encoding='utf-8')) if os.path.exists(AP) else {}
AL.update({o: n for o, n in IDS})
json.dump(AL, open(AP, 'w', encoding='utf-8'), ensure_ascii=False, indent=1, sort_keys=True)
def resolve(k):
    seen = set()
    while k.split('~')[0] in AL and k not in seen:
        seen.add(k); b, _, c = k.partition('~'); k = AL[b] + ('~' + c if c and '~' not in AL[b] else '')
    return k
ALIAS = 'var ID_ALIAS = ' + json.dumps({o: resolve(o) for o in sorted(AL)}, ensure_ascii=False, separators=(',', ':')) + ';'
if 'var ID_ALIAS' in s:
    s = re.sub(r'var ID_ALIAS = \{[^\n]*\};', lambda m: ALIAS, s, count=1)
else:
    s = s.replace('function byId(id){',
                  '/* Anciens codes d\'articles (brand/ids-propres.py) : paniers, listes et favoris déjà enregistrés */\n'
                  + ALIAS + '\n'
                  'function canonId(id){ var k = String(id), cut = k.indexOf(\'~\'), b = cut > 0 ? k.slice(0, cut) : k; return ID_ALIAS[b] ? ID_ALIAS[b] + (cut > 0 ? k.slice(cut) : \'\') : k; }\n'
                  'function canonMap(o){ var r = {}; for (var k in o){ var c = canonId(k); r[c] = typeof o[k] === \'number\' && typeof r[c] === \'number\' ? r[c] + o[k] : o[k]; } return r; }\n'
                  'function byId(id){', 1)
    reps = [
        ("if (c && typeof c==='object') state.cart = c;", "if (c && typeof c==='object') state.cart = canonMap(c);"),
        ("if (l && typeof l==='object' && l.items) state.list = l;", "if (l && typeof l==='object' && l.items){ l.items = canonMap(l.items); state.list = l; }"),
        ("if (f && typeof f==='object') state.favs = f;", "if (f && typeof f==='object') state.favs = canonMap(f);"),
        ("o.i.forEach(function(x){ if (byId(x[0])) items[x[0]] = ", "o.i.forEach(function(x){ x[0] = canonId(x[0]); if (byId(x[0])) items[x[0]] = "),
    ]
    for a, b in reps:
        assert s.count(a) == 1, 'introuvable : ' + a
        s = s.replace(a, b)
open(HTML, 'w', encoding='utf-8').write(s)

# photos, sources des photos HD, vignettes de la page Catalogue
def git_mv(a, b):
    if os.path.exists(os.path.join(ROOT, a)) and not os.path.exists(os.path.join(ROOT, b)):
        subprocess.run(['git', 'mv', a, b], cwd=ROOT, check=True)
for old, new in IDS:
    for suf in ('', '-2', '-3', '-4'):
        git_mv('images/' + old + suf + '.webp', 'images/' + new + suf + '.webp')
    for d in ('images-sans-filigrane',):
        a, b = os.path.join(ROOT, d, old + '.webp'), os.path.join(ROOT, d, new + '.webp')
        if os.path.exists(a) and not os.path.exists(b): os.rename(a, b)
for rel in ('photos/sources.json', 'admin/thumbs.json'):
    p = os.path.join(ROOT, rel)
    if not os.path.exists(p): continue
    d = json.load(open(p, encoding='utf-8')); ch = False
    for old, new in IDS:
        if old in d and new not in d: d[new] = d.pop(old); ch = True
    if ch:
        if rel.startswith('photos'): json.dump(d, open(p, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
        else: json.dump(d, open(p, 'w', encoding='utf-8'), separators=(',', ':'))
print('codes renommés :', len(done), done)
