"""Liens vers l'aménageur de chambre 3D (page /amenageur/, construite par build.js à partir de amenageur/).
   - Accueil : un encart « Aménagez la chambre de bébé en 3D » (affiche du film + bouton vert, pas de deuxième bouton orange).
   - Fiches des lits, berceaux, lits parapluie, parcs, tables à langer et meubles de rangement : un lien discret.
   Idempotent : se relance sans rien dupliquer."""
import os
P = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'petit-baobab.html')
s = open(P, encoding='utf-8').read()

def rep(old, new, marker):
    global s
    if marker in s: return
    assert s.count(old) == 1, ('introuvable ou multiple', old[:80])
    s = s.replace(old, new)

# 1) Accueil : après « Nouveautés »
rep('''    <div class="grid" id="best"></div>
  </div>
''', '''    <div class="grid" id="best"></div>
  </div>

  <div class="wrap section">
    <a class="planner-card" href="/amenageur/">
      <img src="/amenageur/demo-poster.jpg" alt="" loading="lazy" width="135" height="240">
      <div><span class="kicker">Nouveau</span><h2>Aménagez la chambre de bébé en 3D</h2><p>Entrez les mesures de la pièce, placez les lits, armoires et commodes de la boutique sur un plan et en 3D, et vérifiez que tout rentre avant de commander.</p><span class="btn btn-brand">Essayer l'aménageur</span></div>
    </a>
  </div>
''', 'class="planner-card"')

# 2) Fiche article : lien sous les caractéristiques
rep("""    (p.specs && p.specs.length ? '<dl class="specs">' + p.specs.map(function(x){ return '<dt>' + esc(x[0]) + '</dt><dd>' + esc(x[1]) + '</dd>'; }).join('') + '</dl>' : '') +
""", """    (p.specs && p.specs.length ? '<dl class="specs">' + p.specs.map(function(x){ return '<dt>' + esc(x[0]) + '</dt><dd>' + esc(x[1]) + '</dd>'; }).join('') + '</dl>' : '') +
    (['lits-bebe', 'berceaux', 'lits-parapluie', 'parc-eveil', 'tables-langer', 'mobilier'].indexOf(p.cat) >= 0 ? '<a class="planner-link" href="/amenageur/">Vérifier la place dans la chambre avec l\\'aménageur 3D</a>' : '') +
""", 'class="planner-link"')

# 4) Onglet « Chambre 3D » dans le menu (ordinateur et téléphone), après « Cadeaux »
rep("var NAV = ['accueil','boutique','packs','liste','cadeaux','conseils','livraison'];",
    "var NAV = ['accueil','boutique','packs','liste','cadeaux','amenageur','conseils','livraison'];   // amenageur = page à part (/amenageur/)",
    "'cadeaux','amenageur'")
rep("""  $('#nav').innerHTML = NAV.map(function(v){ return '<a href="' + href(v) + '" data-action="nav" data-view="' + v + '">' + esc(ROUTES[v].nav) + '</a>'; }).join('');""",
    """  $('#nav').innerHTML = NAV.map(function(v){ if (v === 'amenageur') return '<a href="/amenageur/">Chambre 3D</a>'; return '<a href="' + href(v) + '" data-action="nav" data-view="' + v + '">' + esc(ROUTES[v].nav) + '</a>'; }).join('');""",
    "if (v === 'amenageur') return '<a href=\"/amenageur/\">Chambre 3D</a>';")
rep("""  var links = NAV.map(function(v){ return '<a href="' + href(v) + '" data-action="nav" data-view="' + v + '"' + (state.view===v ? ' class="active"' : '') + '>' + esc(ROUTES[v].nav) + icon('chev') + '</a>'; }).join('');""",
    """  var links = NAV.map(function(v){ if (v === 'amenageur') return '<a href="/amenageur/">Chambre 3D' + icon('chev') + '</a>'; return '<a href="' + href(v) + '" data-action="nav" data-view="' + v + '"' + (state.view===v ? ' class="active"' : '') + '>' + esc(ROUTES[v].nav) + icon('chev') + '</a>'; }).join('');""",
    "if (v === 'amenageur') return '<a href=\"/amenageur/\">Chambre 3D' + icon('chev')")

# 3) Styles
CSS = """
/* Aménageur 3D (brand/amenageur-liens.py) */
.planner-card{display:grid;grid-template-columns:96px minmax(0,1fr);gap:16px;align-items:center;background:var(--surface);border:1px solid var(--line);border-radius:var(--radius);padding:14px;color:inherit;text-decoration:none}
.planner-card img{width:96px;height:auto;aspect-ratio:9/16;object-fit:cover;border-radius:12px;display:block;background:var(--brand)}
.planner-card h2{margin:4px 0 6px}
.planner-card p{margin:0 0 12px;color:var(--muted);max-width:60ch}
.planner-card:hover h2{text-decoration:underline}
@media (min-width:700px){.planner-card{grid-template-columns:135px minmax(0,1fr);gap:24px;padding:18px 22px}.planner-card img{width:135px}}
.planner-link{display:inline-block;margin-top:10px;font-weight:700;color:var(--brand);text-decoration:underline;text-underline-offset:3px}
"""
if '/* Aménageur 3D (brand/amenageur-liens.py) */' not in s:
    i = s.index('</style>'); s = s[:i] + CSS + s[i:]

open(P, 'w', encoding='utf-8').write(s)
print('liens aménageur : ok')
