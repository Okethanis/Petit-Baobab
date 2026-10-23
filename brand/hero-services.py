"""Haut de l'accueil : nos services et à qui ils s'adressent, le plus court possible (demande de Hanis, 23 oct. 2026).
   Remplace le long paragraphe sous le titre par une ligne « Pour qui » et une rangée de services cliquables.
   Pas de deuxième bouton orange : les services sont de simples pastilles claires. Idempotent."""
import os
P = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'petit-baobab.html')
s = open(P, encoding='utf-8').read()

OLD = ("        <p class=\"lead\">Packs naissance par budget, valise de maternité prête à partir et tout l'équipement de bébé, "
       "du premier jour aux premiers pas, avec les prix affichés. Vous commandez en ligne, on vous livre à Abidjan en moins de 24\u00a0h.</p>\n")
NEW = ('        <p class="lead hero-for">Pour les futurs parents, les jeunes parents et ceux qui veulent offrir.</p>\n'
       '        <ul class="hero-services" aria-label="Nos services">'
       '<li><a href="#packs" data-action="nav" data-view="packs">Packs naissance</a></li>'
       '<li><a href="#valise" data-action="nav" data-view="valise">Valise de maternité</a></li>'
       '<li><a href="#boutique" data-action="nav" data-view="boutique">Équipement bébé 0-3 ans</a></li>'
       '<li><a href="#liste" data-action="nav" data-view="liste">Liste de naissance</a></li>'
       '<li><a href="#cadeaux" data-action="nav" data-view="cadeaux">Cadeaux de naissance</a></li>'
       '<li><a href="/amenageur/">Chambre en 3D</a></li>'
       '</ul>\n')
if 'class="hero-services"' not in s:
    assert s.count(OLD) == 1, 'paragraphe du haut introuvable'
    s = s.replace(OLD, NEW)

CSS = """
/* Haut de l'accueil : pour qui + services (brand/hero-services.py) */
.hero-for{margin:0;font-weight:600;color:#fff!important}
.hero-services{list-style:none;margin:0;padding:0;display:flex;flex-wrap:wrap;justify-content:center;gap:8px;max-width:640px}
.hero-services a{display:inline-block;padding:6px 13px;border:1px solid rgba(255,255,255,.38);border-radius:999px;color:#fff;text-decoration:none;font-weight:600;font-size:.92rem;line-height:1.3;background:rgba(255,255,255,.06);transition:background .2s,border-color .2s}
.hero-services a:hover,.hero-services a:focus-visible{background:rgba(255,255,255,.16);border-color:rgba(255,255,255,.7)}
"""
if '/* Haut de l\'accueil : pour qui + services' not in s:
    i = s.index('</style>'); s = s[:i] + CSS + s[i:]
open(P, 'w', encoding='utf-8').write(s)
print('haut de l\'accueil : ok')
