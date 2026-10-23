"""Doublons du catalogue (décision de Hanis, 23 oct. 2026 : « efface les doublons », prix le plus haut, couleurs en une fiche).
   - DOUBLONS : même article sous plusieurs codes → on garde une fiche (la mieux renseignée : photos HD, packs…),
     les autres passent en hidden:true (rien n'est supprimé, on peut revenir en arrière), prix = le plus haut du groupe.
   - COULEURS : même modèle en plusieurs couleurs → une fiche avec choix de couleur (champ colors, brand/couleurs.py),
     les autres fiches passent en hidden:true.
   - Les anciens codes vont dans brand/alias.json → ID_ALIAS : paniers, favoris et listes de naissance déjà enregistrés
     pointent vers la fiche gardée (et la bonne couleur).
   - Les packs qui contenaient un doublon pointent vers la fiche gardée.
   Ensuite : python3 -I brand/couleurs.py && node admin/packs.js && node build.js
   Relançable sans rien dupliquer."""
import json, os, re

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
HTML = os.path.join(ROOT, 'petit-baobab.html')

# (fiche gardée, [doublons cachés], prix retenu = le plus haut du groupe)
DOUBLONS = [
    ('020', ['020-2'], 25500),
    ('0212-18', ['1632-2'], 1100),
    ('0212-40', ['11202-2'], 142500),
    ('11', ['10'], 10500),
    ('111', ['111-307', 'kjc-111'], 71300),
    ('11202-1', ['1632-5', '0212-8'], 20700),
    ('136-1', ['7276-5'], 31900),
    ('153d', ['153d-1571', 'd1571'], 121900),
    ('158d', ['d1581'], 121900),
    ('1656-1', ['7276-3', '136-2'], 1700),
    ('1656-15', ['23-46'], 4400),
    ('2001', ['2001-net'], 17300),
    ('2151-3', ['7276-4', '1656-2'], 2700),
    ('2151-4', ['7276-7'], 5200),
    ('230', ['2301'], 91900),
    ('262', ['2621', 'p2621'], 112500),
    ('2631', ['p263', 'p2631'], 112500),
    ('271', ['p271'], 120000),
    ('307', ['307-color-box'], 56300),
    ('6051', ['6052'], 10400),
    ('616', ['bkd616'], 48800),
    ('7025', ['7025wax'], 86300),
    ('7025ydx', ['7025ygx'], 86300),
    ('709', ['8709-with-light'], 181900),
    ('7276-2', ['1656-8'], 11900),
    ('7532-2', ['7532-b'], 116300),
    ('8104', ['08104'], 83300),
    ('8105', ['08105'], 76900),
    ('8106', ['08106'], 76900),
    ('8966', ['08966'], 156800),
    ('bc009', ['bc009-color-box'], 43200),
    ('bjj-708-color-box', ['bjj-708l-color-box'], 156800),
    ('bn001', ['bn001-net'], 28200),
    ('bn007', ['bn007-net'], 35700),
    ('c209', ['bkd001'], 63800),
    ('hh727', ['hh727-b'], 43200),
    ('kbh607s', ['kbh608s'], 149300),
    ('kdd205', ['kddbb205'], 43200),
    ('kdd305', ['kdd305-color-box'], 46900),
    ('kddbb-9', ['kjc-9'], 75000),
    ('kddyw2004', ['y04-with-light', '5704-with-light'], 183800),
    ('kjc-1b', ['kjc-1', 'kjc-1-color-box'], 51800),
    ('sf-24', ['sf-24-n'], 18800),
    ('tm716', ['tm716-b'], 219400),
    ('xj-8332', ['xj8332'], 6400),
    ('xj8330', ['xj-8330'], 6400),
]

# (fiche gardée, [(couleur, code de la fiche de cette couleur)], prix) — la 1re couleur est celle de la fiche gardée
# 08113 (91 900) reste une fiche à part : son prix est très différent de 08112 / 08114 (81 800).
COULEURS = [
    ('p270', [('Blanc', 'p270'), ('Bois naturel', '270')], 120000),
    ('bjj-008p', [('Kaki', 'bjj-008p'), ('Blanc', 'bjj008p')], 125700),
    ('08303', [('Gris', '08303'), ('Mauve', '08305')], 131300),
    ('8207', [('Lamas', '8207'), ('Pingouins', '8208'), ('Gris rayé', '8209')], 82500),
    ('8104', [('Gris clair', '8104'), ('Gris foncé', '8105'), ('Mauve', '8106')], 83300),
    ('08112', [('Gris foncé', '08112'), ('Gris clair', '08114')], 81800),
    ('8085', [('Gris', '8085'), ('Gris foncé', '8087'), ('Beige', '08081')], 81800),
    ('f7025', [('Bleu', 'f7025'), ('Rose', 'g7025')], 86300),
    ('668-34', [('Multicolore', '668-34'), ('Rose', '668-35')], 35700),
    ('6037', [('Vert', '6037'), ('Rose', '6033')], 69400),
    ('np-002', [('Bleu', 'np-002'), ('Blanc', 'np-003')], 13900),
]

s = open(HTML, encoding='utf-8').read()
i0 = s.index('var PRODUCTS = [\n'); i1 = s.index('\n];', i0)
block = s[i0:i1]

def line(pid):
    m = re.search(r"^  \{id:'" + re.escape(pid) + r"',[^\n]*$", block, re.M)
    assert m, 'article introuvable : ' + pid
    return m.group(0)

def put(old, new):
    global block
    if old != new: block = block.replace(old, new, 1)

def hide(pid):
    l = line(pid)
    if 'hidden:true' not in l: put(l, re.sub(r'\}(,?)$', r', hidden:true}\1', l))

def price(pid, p):
    l = line(pid)
    put(l, re.sub(r"(, price:)\d+", lambda m: m.group(1) + str(p), l, count=1))

alias = {}
VARIANTES = {pid for _, cols, _ in COULEURS for _, pid in cols[1:]}   # 8105, 8106 : gardées comme doublons, puis couleurs de 8104
for keep, dups, p in DOUBLONS:
    assert 'hidden:true' not in line(keep) or keep in VARIANTES, keep
    price(keep, p)
    for d in dups: hide(d); alias[d] = keep
for keep, cols, p in COULEURS:
    assert 'hidden:true' not in line(keep), keep
    price(keep, p)
    for name, pid in cols[1:]: hide(pid); alias[pid] = keep + '~' + name

# packs et valises : un doublon dans la composition → la fiche gardée
for l in re.findall(r"^  \{id:'[^']+',[^\n]*items:\[[^\n]*$", block, re.M):
    n = l
    for old, new in alias.items():
        new = new.split('~')[0]
        if "{id:'" + old + "', qty:" in n:
            assert "{id:'" + new + "', qty:" not in n, (old, new)
            n = n.replace("{id:'" + old + "', qty:", "{id:'" + new + "', qty:")
    put(l, n)

s = s[:i0] + block + s[i1:]

# anciens codes → fiche gardée (brand/alias.json partagé avec brand/ids-propres.py)
AP = os.path.join(ROOT, 'brand', 'alias.json')
AL = json.load(open(AP, encoding='utf-8')) if os.path.exists(AP) else {}
AL.update(alias)
json.dump(AL, open(AP, 'w', encoding='utf-8'), ensure_ascii=False, indent=1, sort_keys=True)
def resolve(k):
    seen = set()
    while k.split('~')[0] in AL and k not in seen:
        seen.add(k); b, _, c = k.partition('~'); k = AL[b] + ('~' + c if c and '~' not in AL[b] else '')
    return k
ALIAS = 'var ID_ALIAS = ' + json.dumps({o: resolve(o) for o in sorted(AL)}, ensure_ascii=False, separators=(',', ':')) + ';'
assert 'var ID_ALIAS' in s, 'lancer d\'abord brand/ids-propres.py'
s = re.sub(r'var ID_ALIAS = \{[^\n]*\};', lambda m: ALIAS, s, count=1)
open(HTML, 'w', encoding='utf-8').write(s)
print('doublons : %d fiches gardées, %d cachées ; couleurs : %d fiches' % (len(DOUBLONS), sum(len(d) for _, d, _ in DOUBLONS), len(COULEURS)))
