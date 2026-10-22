# Petit Baobab, le site

Dépôt relié à Netlify : chaque modification poussée ici reconstruit et publie le site automatiquement (une à deux minutes).

## Ce qu'il y a dedans

- `petit-baobab.html` : la page complète (textes, catalogue, réglages). C'est le seul fichier à modifier à la main.
  - bloc `CONFIG` : numéro WhatsApp de la marque (encore un numéro fictif, à remplacer), frais par commune, moyens de paiement, raison sociale et RCCM, mesure d'audience
  - blocs `UNIVERS` et `CATS` : les 8 univers et leurs catégories
  - bloc `PRODUCTS` : les articles (nom, prix, référence, catégorie, description, photo) et les packs (composition, remise)
- `images/` : les photos des produits (WebP, avec filigrane)
- `static/` : favicons et image de partage déjà rendus
- `build.js` : fabrique le dossier `site/` que Netlify publie (une adresse par page, 404, sitemap, robots, image de partage…). Netlify le lance tout seul (`netlify.toml`).
- `admin/` : la page Catalogue (modification des prix) et le Tableau de bord, avec les scripts qui les génèrent
- `brand/` : logo, charte, animation du logo (scripts Python et Node)

## Modifier un prix, un texte, une photo

1. Ouvrir `petit-baobab.html` sur GitHub, cliquer sur le crayon, modifier, puis « Commit changes ».
2. Netlify reconstruit le site tout seul. Rien d'autre à faire.

Pour les prix en série, passer par la page Catalogue, puis reporter les changements avec `node admin/apply-changes.js` et `node admin/packs.js` (ordinateur avec Node.js), et pousser le fichier.

## Reconstruire sur un ordinateur (facultatif)

```
node admin/packs.js
node build.js
```

Le dossier `site/` est recréé (il n'est pas gardé dans le dépôt). Pour ouvrir le site sans rien installer : double-clic sur `petit-baobab.html`.
