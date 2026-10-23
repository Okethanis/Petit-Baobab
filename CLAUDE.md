# Petit Baobab — site de puériculture en ligne (Abidjan)

Boutique en ligne qui présente ~597 articles et conclut les ventes sur **WhatsApp** (pas de paiement en ligne, pas de serveur, pas de base de données). Site statique, en français.

## Comment c'est construit

- **`petit-baobab.html`** : LE fichier source unique. Il contient tout — styles (`<style>`), scripts (`<script>`), les réglages (`var CONFIG`), les adresses des pages (`var ROUTES`), et le catalogue (`var PRODUCTS`, une ligne par article).
- **`build.js`** : génère le dossier `site/` (une vraie page par adresse, 404, sitemap, robots, en-têtes de sécurité `_headers`). Commande : `node build.js`.
- **`images/`** : photos des articles en WebP (avec filigrane « Petit Baobab »).
- **`static/`** : fichiers publiés tels quels (favicons, image de partage).
- **`brand/`** : scripts Python/JS qui modifient `petit-baobab.html` de façon idempotente (police, boutons, pied de page, pages, images de packs…). Chacun se relance sans dupliquer.
- **`admin/`** : la page « Catalogue » (modifier prix/fiches) et le « Tableau de bord » (registre des commandes). Ce sont des artefacts claude.ai séparés, PAS publiés sur le site. Générés par `make-admin.js` / `make-dashboard.js`. Non versionnés (voir `.gitignore`).

## Pour voir le site en local

```
node build.js
cd site && python3 -m http.server 8000   # puis ouvrir http://localhost:8000
```

## Mise en ligne (ATTENTION aux crédits)

- Hébergé sur **Netlify** (plan gratuit : **300 crédits/mois**, cycle du 22 au 21). Chaque mise en ligne du site = **15 crédits**. Le site est coupé si on atteint 300.
- Déploiement automatique : `git push` sur la branche `main` du dépôt `Okethanis/Petit-Baobab` → Netlify reconstruit.
- `netlify.toml` ne reconstruit QUE si `petit-baobab.html`, `build.js`, `images`, `static` ou `vendor` changent. Un commit qui ne touche que `admin/`, `brand/`, `CLAUDE.md` ne coûte rien.
- **Travailler sur une branche et ouvrir une Pull Request** donne un aperçu gratuit (`deploy-preview-N--petit-baobab.netlify.app`) sans dépenser de crédits. Ne fusionner dans `main` que quand c'est validé.
- Envisager **Cloudflare Pages** (gratuit, sans crédits) avant le lancement public (TikTok, pub).

## Conventions

- Tout en français. Un seul bouton orange par page. Prix « 54 500 FCFA » avec espace fine.
- Aucune donnée sensible publiée : pas de prix d'achat, pas de packing list, pas d'adresse.
- Vérifier après chaque modif du script : `node -e "..."` pour contrôler que les `<script>` sont valides, et `node build.js` sans erreur.

## À faire (au 23 oct. 2026)

- Remplacer les **tarifs de livraison** par commune (dans `CONFIG.zones`) par les vrais tarifs.
- Remplacer l'**adresse e-mail** fictive (`CONFIG.email`) par la vraie.
- Nom de domaine souhaité : `petit-baobab.com`.
