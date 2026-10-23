"""23 oct. 2026 — supprime les références fournisseur en chinois (champ `ref` des articles).
   Ces références venaient des packing lists et s'affichaient sur le site (« Réf. 袜子 »), parfois avec
   des quantités par coloris (« 米30 灰50 兰20 »). Demande de Hanis : « Supprime les réf chinoises ».
   Si, une fois les caractères chinois retirés, il reste un vrai code (lettres + chiffres, ex. « 香槟-BW365 » -> « BW365 »),
   on garde ce code ; sinon la référence est retirée (le site n'affiche alors pas de ligne « Réf. »).
   Idempotent : se relance sans rien changer une fois fait."""
import os, re
HERE = os.path.dirname(os.path.abspath(__file__))
P = os.path.join(HERE, '..', 'petit-baobab.html')
s = open(P, encoding='utf-8').read()

CJK = re.compile(r'[　-〿㐀-鿿＀-￯]')
CODE = re.compile(r'^[A-Za-z]{2,}\d{2,}$')

i0 = s.index('var PRODUCTS'); i1 = s.index('\n];', i0)
block = s[i0:i1]
kept, removed = [], []

def fix(m):
    ref = m.group(2)
    if not CJK.search(ref):
        return m.group(0)
    rest = re.sub(r'^[^A-Za-z0-9]+|[^A-Za-z0-9]+$', '', CJK.sub(' ', ref)).strip()
    if CODE.match(rest):
        kept.append((ref, rest))
        return m.group(1) + "ref:'" + rest + "'"
    removed.append(ref)
    return ''

# « , ref:'…' » (la référence n'est jamais le premier champ d'une ligne d'article)
block = re.sub(r"(, )ref:'((?:[^'\\]|\\.)*)'", fix, block)
s = s[:i0] + block + s[i1:]

left = CJK.findall(s[i0:s.index('\n];', i0)])
assert not left, ('caractères chinois restants dans PRODUCTS', ''.join(left)[:60])

open(P, 'w', encoding='utf-8').write(s)
print('références gardées sans le chinois :', ', '.join(b for a, b in kept) or 'aucune')
print('références supprimées :', len(removed))
